from typing import Dict, Any
from .base import Agent
from utils.exceptions import ProcessingError

class DefaultAgent(Agent):
    async def execute(self, input_data: str) -> str:
        """Дефолтная обработка запроса"""
        try:
            return input_data  
        except Exception as e:
            raise ProcessingError(f"Default processing failed: {str(e)}") from e