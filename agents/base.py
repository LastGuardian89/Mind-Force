from abc import ABC, abstractmethod
from typing import Any, Dict
from utils.exceptions import ProcessingError

class Agent(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._validate_config()
        
    def _validate_config(self):
        """Проверка конфигурации агента"""
        required_params = self.required_params()
        for param in required_params:
            if param not in self.config:
                raise ProcessingError(f"Missing required parameter: {param}")

    @staticmethod
    @abstractmethod
    def required_params() -> list:
        """Список обязательных параметров конфигурации"""
        return []

    @abstractmethod
    async def execute(self, input_data: str) -> str:
        """Основной метод выполнения задачи"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} config={self.config}>"