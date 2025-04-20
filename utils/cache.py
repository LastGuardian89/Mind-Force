import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class SmartCache:
    def __init__(self, cache_dir: str = "cache", ttl: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl  # Время жизни записи в секундах (по умолчанию 24 часа)
        self._init_cache_dir()

    def _init_cache_dir(self):
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def _get_key_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def generate_key(
        self,
        prompt: str,
        context: str,
        model_version: str,
        data_hash: str
    ) -> str:
        """Генерация уникального ключа кэша"""
        key_data = f"{prompt}-{context}-{model_version}-{data_hash}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def check_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Проверка наличия записи в кэше"""
        key_path = self._get_key_path(key)
        
        if not key_path.exists():
            return None

        with open(key_path, 'r') as f:
            entry = json.load(f)
            
        if self._is_expired(entry['timestamp']):
            key_path.unlink()
            return None
            
        return entry['response']

    def save_cache(
        self,
        key: str,
        response: str,
        metadata: Optional[Dict] = None
    ):
        """Сохранение записи в кэш"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'metadata': metadata or {}
        }
        
        with open(self._get_key_path(key), 'w') as f:
            json.dump(entry, f)

    def _is_expired(self, timestamp: str) -> bool:
        """Проверка истечения срока жизни записи"""
        entry_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - entry_time).total_seconds() > self.ttl

class DataHasher:
    @staticmethod
    def hash_content(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @classmethod
    def hash_file(cls, file_path: Path) -> str:
        with open(file_path, 'rb') as f:
            return cls.hash_content(f.read())

    @classmethod
    def hash_code(cls, code: str) -> str:
        return cls.hash_content(code.encode())

class CacheManager:
    def __init__(self, model: PhiLLM): #? Решить вопрос с PhiLLM
        self.cache = SmartCache()
        self.model = model
        self.hasher = DataHasher()

    async def process_request(
        self,
        prompt: str,
        context: str,
        data_source: Optional[Path] = None,
        code: Optional[str] = None
    ) -> Optional[str]:
        data_hash = self._get_data_hash(data_source, code)
        
        cache_key = self.cache.generate_key(
            prompt=prompt,
            context=context,
            model_version=self.model.version,
            data_hash=data_hash
        )
        
        if cached := self.cache.check_cache(cache_key):
            return cached
        
        return None

    def _get_data_hash(
        self,
        data_source: Optional[Path],
        code: Optional[str]
    ) -> str:
        if data_source:
            return self.hasher.hash_file(data_source)
        if code:
            return self.hasher.hash_code(code)
        return "no_data"

async def handle_user_request(prompt: str, context: str, file_path: Path):
    model = PhiLLM()
    cache_manager = CacheManager(model)
    
    cached_response = await cache_manager.process_request(
        prompt=prompt,
        context=context,
        data_source=file_path
    )
    
    if cached_response:
        return cached_response
    
    response = await process_request(prompt, context, file_path)
    
    cache_manager.cache.save_cache(
        key=cache_manager.cache.generate_key(
            prompt=prompt,
            context=context,
            model_version=model.version,
            data_hash=cache_manager.hasher.hash_file(file_path)
        ),
        response=response,
        metadata={
            'source': str(file_path),
            'model_version': model.version
        }
    )
    
    return response