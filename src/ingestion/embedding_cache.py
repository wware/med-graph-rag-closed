# src/ingestion/embedding_cache.py
import redis
import hashlib
import json
from typing import Optional, List

class EmbeddingCache:
    def __init__(self, redis_url='redis://localhost:6379'):
        self.redis = redis.from_url(redis_url)
    
    def get(self, text: str, model: str = 'titan_v2') -> Optional[List[float]]:
        key = f"emb:{model}:{hashlib.md5(text.encode()).hexdigest()}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, text: str, embedding: List[float], model: str = 'titan_v2'):
        key = f"emb:{model}:{hashlib.md5(text.encode()).hexdigest()}"
        self.redis.setex(key, 86400*30, json.dumps(embedding))  # 30 day TTL
