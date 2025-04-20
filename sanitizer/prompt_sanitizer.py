import re
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from typing import Optional
from utils.exceptions import InjectionAttemptError, SecurityException

class PromptSanitizer:
    def __init__(self, model_path: str = "bert-prompt-sanitizer"):
        self.patterns = [
            (r'(?i)(delete|drop|truncate)', "SQL injection"),
            (r'<script.*?>', "HTML injection"),
            (r'\{%|%\}', "Template injection"),
            (r'__import__|eval\(|exec\(', "Code injection"),
            (r'(ftp|ssh|sftp)://', "Dangerous protocol"),
            (r'/etc/passwd', "Sensitive file access")
        ]
        
        try:
            self.tokenizer = BertTokenizer.from_pretrained(model_path)
            self.model = BertForSequenceClassification.from_pretrained(model_path).eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load security model: {str(e)}")

    def sanitize(self, prompt: str) -> str:
        self._check_patterns(prompt)
        self._check_ml(prompt)
        return prompt

    def _check_patterns(self, text: str):
        for pattern, description in self.patterns:
            if re.search(pattern, text):
                raise InjectionAttemptError(f"Pattern detected: {description} - {pattern}")

    def _check_ml(self, text: str):
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probs = torch.softmax(outputs.logits, dim=1)
            if probs[0][1].item() > 0.85:
                raise SecurityException("ML model detected malicious intent")
                
        except Exception as e:
            raise SecurityException(f"Security check failed: {str(e)}")

class SanitizationPipeline:
    @staticmethod
    async def process(prompt: str) -> str:
        try:
            sanitizer = PromptSanitizer()
            return sanitizer.sanitize(prompt)
        except Exception as e:
            raise SecurityException(str(e))