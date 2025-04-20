import re
import mimetypes
from typing import Optional
from .base import Agent
from .pdf_link_agent import PDFLinkAgent
from .code_exec_agent import CodeExecutionAgent
from .pdf_file_agent import PDFFileAgent
from .default_agent import DefaultAgent
from utils.exceptions import AgentSelectionError, SecurityException

class AgentSelector:
    def __init__(self):
        self.code_patterns = [
            r'(def\s+\w+\s*\(.*\):)',
            r'(class\s+\w+)',
            r'(import\s+\w+)',
            r'(print\(.*\))',
            r'(\#\!.*python)'
        ]
        self.url_pattern = r'(https?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.pdf)'

    def select_agent(self, prompt: str) -> Agent:
        try:
            # Проверка безопасности перед выбором агента
            self._check_prompt_safety(prompt)
            
            # Определение типа задачи
            if self._is_pdf_url(prompt):
                return PDFLinkAgent()
                
            if self._is_code(prompt):
                return CodeExecutionAgent()
                
            if self._has_uploaded_file(prompt):
                return self._handle_file_upload(prompt)
                
            return DefaultAgent()
            
        except Exception as e:
            raise AgentSelectionError(f"Agent selection failed: {str(e)}")

    def _check_prompt_safety(self, prompt: str):
        forbidden_patterns = [
            r'(\/etc\/passwd)',
            r'(file:\/\/)',
            r'(localhost:\d+)'
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, prompt):
                raise SecurityException(f"Dangerous pattern detected: {pattern}")

    def _is_pdf_url(self, text: str) -> bool:
        return bool(re.search(self.url_pattern, text))

    def _is_code(self, text: str) -> bool:
        return any(re.search(pattern, text) for pattern in self.code_patterns)

    def _has_uploaded_file(self, text: str) -> bool:
        return '<uploaded_file>' in text

    def _handle_file_upload(self, prompt: str) -> Agent:
        file_info = self._parse_upload(prompt)
        mime_type, _ = mimetypes.guess_type(file_info['name'])
        
        if mime_type == 'application/pdf':
            return PDFFileAgent()
        elif mime_type in ['text/plain', 'text/x-python']:
            return CodeExecutionAgent()
            
        raise AgentSelectionError(f"Unsupported file type: {mime_type}")

    def _parse_upload(self, prompt: str) -> dict:
        match = re.search(r'<uploaded_file>(?P<name>.+?)</uploaded_file>', prompt)
        if not match:
            raise AgentSelectionError("Invalid file upload format")
        return {'name': match.group('name')}