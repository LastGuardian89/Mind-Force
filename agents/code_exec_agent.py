import re
from typing import Dict, Any
from .base import Agent
from utils.docker_sandbox import DockerSandbox
from utils.exceptions import (CodeExecutionError, ResourceLimitExceeded,
                         DockerSecurityException)

class CodeExecutionAgent(Agent):
    MAX_OUTPUT_LENGTH = 10000
    BLACKLIST_PATTERNS = [
        r"os\.system",
        r"subprocess\.",
        r"open\(",
        r"import\s+(os|sys|subprocess)",
        r"__import__",
        r"eval\(",
        r"exec\(",
        r"pickle\.",
        r"shutil\.",
        r"socket\."
    ]

    @staticmethod
    def required_params():
        return ["docker_config"]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sandbox = DockerSandbox(config["docker_config"])
        
    async def execute(self, input_data: str) -> str:
        """Безопасное выполнение кода"""
        try:
            self._validate_code(input_data)
            result = await self.sandbox.execute(input_data)
            return self._sanitize_output(result)
        except DockerSecurityException as e:
            raise CodeExecutionError(f"Security violation: {str(e)}") from e
        except Exception as e:
            raise CodeExecutionError(str(e)) from e

    def _validate_code(self, code: str):
        """Проверка кода на опасные паттерны"""
        for pattern in self.BLACKLIST_PATTERNS:
            if re.search(pattern, code):
                raise DockerSecurityException(f"Blocked pattern: {pattern}")

    def _sanitize_output(self, output: str) -> str:
        """Санобработка вывода"""
        if len(output) > self.MAX_OUTPUT_LENGTH:
            raise ResourceLimitExceeded("Output too large")
            
        # Удаление чувствительной информации
        cleaned = re.sub(r"(API_KEY|SECRET|PASSWORD)\s*=\s*'.*?'", "[REDACTED]", output)
        return cleaned[:self.MAX_OUTPUT_LENGTH]