import fitz
import os
from pathlib import Path
from typing import Dict, Any
from .base import Agent
from utils.exceptions import PDFProcessingError, ResourceLimitExceeded

class PDFFileAgent(Agent):
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_MIME_TYPES = ["application/pdf"]
    
    @staticmethod
    def required_params():
        return ["upload_dir", "embedding_model"]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.upload_dir = Path(config["upload_dir"])
        self.embedding_model = config["embedding_model"]
        self._validate_upload_dir()

    def _validate_upload_dir(self):
        """Проверка директории для загрузок"""
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True)
        if not os.access(self.upload_dir, os.W_OK):
            raise PDFProcessingError("Upload directory not writable")

    async def execute(self, input_data: str) -> str:
        """Обработка загруженного PDF"""
        try:
            file_path = self._validate_file(input_data)
            text = self._parse_pdf(file_path)
            return self._find_relevant_sections(text, input_data)
        except Exception as e:
            raise PDFProcessingError(str(e)) from e

    def _validate_file(self, input_data: str) -> Path:
        """Валидация загруженного файла"""
        file_match = re.search(r"<uploaded_file>(.+?)</uploaded_file>", input_data)
        if not file_match:
            raise PDFProcessingError("Invalid file format")
            
        file_path = self.upload_dir / file_match.group(1)
        if not file_path.exists():
            raise PDFProcessingError("File not found")
            
        if file_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ResourceLimitExceeded("File size exceeds limit")
            
        return file_path

    def _parse_pdf(self, file_path: Path) -> str:
        """Парсинг PDF файла"""
        try:
            doc = fitz.open(file_path)
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