import re
import requests
import fitz
from io import BytesIO
from typing import Optional
from sentence_transformers import util
from .base import Agent
from utils.exceptions import (PDFProcessingError, NetworkError, 
                         ResourceLimitExceeded, SecurityException)

class PDFLinkAgent(Agent):
    MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
    TIMEOUT = 15
    
    @staticmethod
    def required_params():
        return ["embedding_model"]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.embedding_model = config["embedding_model"]
        
    async def execute(self, input_data: str) -> str:
        """Основной метод обработки PDF по ссылке"""
        try:
            url = self._extract_url(input_data)
            content = await self._download_pdf(url)
            text = self._parse_pdf(content)
            return self._find_relevant_sections(text, input_data)
        except Exception as e:
            raise PDFProcessingError(str(e)) from e

    def _extract_url(self, text: str) -> str:
        """Извлечение PDF URL из текста"""
        match = re.search(r'(https?://\S+\.pdf)', text)
        if not match:
            raise PDFProcessingError("No valid PDF URL found")
        return match.group(1)

    async def _download_pdf(self, url: str) -> bytes:
        """Безопасная загрузка PDF"""
        try:
            async with requests.Session() as session:
                response = await session.get(
                    url,
                    stream=True,
                    timeout=self.TIMEOUT,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                response.raise_for_status()

                if int(response.headers.get('Content-Length', 0)) > self.MAX_PDF_SIZE:
                    raise ResourceLimitExceeded("PDF file size exceeds limit")

                return await response.content.read()

        except requests.RequestException as e:
            raise NetworkError(f"Failed to download PDF: {str(e)}") from e

    def _parse_pdf(self, content: bytes) -> str:
        """Парсинг PDF контента"""
        try:
            with BytesIO(content) as buffer:
                doc = fitz.open("pdf", buffer)
                return "\n".join([page.get_text() for page in doc])
        except fitz.FileDataError:
            raise PDFProcessingError("Invalid PDF file structure")
        except Exception as e:
            raise PDFProcessingError(f"PDF parsing error: {str(e)}")

    def _find_relevant_sections(self, text: str, query: str) -> str:
        """Поиск релевантных разделов"""
        try:
            chunks = text.split("\n\n")
            query_embedding = self.embedding_model.encode(query)
            doc_embeddings = self.embedding_model.encode(chunks)
            
            scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]
            top_indices = scores.argsort(descending=True)[:5]
            
            return "\n".join([chunks[i] for i in top_indices])
        except Exception as e:
            raise PDFProcessingError(f"Relevance search failed: {str(e)}")