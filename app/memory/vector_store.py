import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

class VectorStore:
    def __init__(self, dimension: int = 384, storage_path: str = ".cache/vectors"):
        self.dimension = dimension
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self.index = 0
    
    def add(self, text: str, vector: Optional[np.ndarray] = None, metadata: Dict[str, Any] = None):
        if vector is None:
            vector = self._simple_embed(text)
        
        key = f"vec_{self.index}"
        self.vectors[key] = vector
        self.metadata[key] = {
            "text": text,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        self.index += 1
        return key
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self._simple_embed(query)
        
        similarities = []
        for key, vector in self.vectors.items():
            sim = self._cosine_similarity(query_vector, vector)
            similarities.append((key, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for key, score in similarities[:top_k]:
            results.append({
                "key": key,
                "score": float(score),
                "metadata": self.metadata[key]
            })
        
        return results
    
    def _simple_embed(self, text: str) -> np.ndarray:
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.dimension).astype(np.float32)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def save(self):
        data = {
            "vectors": {k: v.tolist() for k, v in self.vectors.items()},
            "metadata": self.metadata,
            "index": self.index
        }
        with open(self.storage_path / "store.json", "w") as f:
            json.dump(data, f)
    
    def load(self):
        path = self.storage_path / "store.json"
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
            self.vectors = {k: np.array(v) for k, v in data["vectors"].items()}
            self.metadata = data["metadata"]
            self.index = data["index"]
