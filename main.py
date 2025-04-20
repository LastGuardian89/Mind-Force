import asyncio
from typing import Optional
from agents.selector import AgentSelector
from .llm.phi_wrapper import PhiLLM
from .society_mind.autogen_society import SocietyMind
from .sanitizer.prompt_sanitizer import SanitizationPipeline
from .utils.io import get_input_data, send_response, log_request
from .utils.cache import check_cache, save_cache
from .utils.logger import setup_logging, RequestLogger
from utils.exceptions import (SecurityException, ProcessingError, 
                        NetworkError, ResourceLimitExceeded)

class AIOrchestrator:
    def __init__(self):
        setup_logging()
        self.logger = RequestLogger()
        self.selector = AgentSelector()
        self.llm = PhiLLM()
        self.society = SocietyMind(self.llm)
        self.cache_enabled = True

    async def process_request(self, user_input: str) -> str:
        try:
            # Шаг 1: Санитайзинг ввода
            clean_input = await SanitizationPipeline.process(user_input)
            
            # Шаг 2: Проверка кэша
            if self.cache_enabled:
                cached = check_cache(clean_input)
                if cached:
                    self.logger.log("CACHE_HIT", {"input": clean_input})
                    return cached

            # Шаг 3: Выбор и выполнение агента
            agent = self.selector.select_agent(clean_input)
            context = await agent.execute(clean_input)
            
            # Шаг 4: Генерация ответа
            raw_response = await self.llm.generate_async(clean_input, context)
            
            # Шаг 5: Обсуждение в SocietyMind
            final_response = await self.society.refine(
                prompt=clean_input,
                context=context,
                initial_response=raw_response
            )

            # Шаг 6: Сохранение и возврат результата
            save_cache(clean_input, final_response)
            return final_response

        except SecurityException as e:
            self.logger.log("SECURITY_BLOCK", {
                "input": user_input,
                "reason": str(e)
            })
            return "Request blocked for security reasons"
            
        except ProcessingError as e:
            self.logger.log("PROCESSING_ERROR", {
                "input": user_input,
                "error": str(e)
            })
            return "Error processing your request"
            
        except Exception as e:
            self.logger.log("INTERNAL_ERROR", {
                "input": user_input,
                "error": str(e)
            })
            return "Internal server error"

        finally:
            log_request(user_input, final_response if 'final_response' in locals() else None)

async def main_flow():
    orchestrator = AIOrchestrator()
    while True:
        try:
            user_input = get_input_data()
            response = await orchestrator.process_request(user_input)
            send_response(response)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    asyncio.run(main_flow())