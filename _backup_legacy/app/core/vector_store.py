"""Vector database abstraction layer"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from app.core.config import get_config
from app.core.logger import setup_logger


logger = setup_logger(__name__)


class VectorStore(ABC):
    """Abstract vector store interface"""
    
    @abstractmethod
    async def add(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """Add texts with metadata"""
        pass
    
    @abstractmethod
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts"""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """Delete entries"""
        pass


class MilvusStore(VectorStore):
    """Milvus vector store implementation"""
    
    def __init__(self):
        self.config = get_config()
        try:
            from pymilvus import connections, Collection
            self.connections = connections
            self.Collection = Collection
            
            self.connections.connect(
                alias="default",
                host=self.config.milvus_host,
                port=self.config.milvus_port
            )
            logger.info("Connected to Milvus")
        except Exception as e:
            logger.error(f"Milvus connection error: {e}")
            raise
    
    async def add(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """Add texts to Milvus"""
        from app.core.llm_client import get_llm_client
        
        llm = get_llm_client()
        embeddings = []
        
        for text in texts:
            embedding = await llm.embed(text)
            embeddings.append(embedding)
        
        # Insert into collection
        collection = self.Collection("documents")
        ids = collection.insert([embeddings, texts, metadatas])
        
        logger.info(f"Added {len(ids)} documents to Milvus")
        return ids
    
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search Milvus"""
        from app.core.llm_client import get_llm_client
        
        llm = get_llm_client()
        query_embedding = await llm.embed(query)
        
        collection = self.Collection("documents")
        results = collection.search(
            [query_embedding],
            "embedding",
            {"metric_type": "L2"},
            limit=k
        )
        
        return [
            {
                "text": hit.entity.get("text"),
                "metadata": hit.entity.get("metadata"),
                "distance": hit.distance
            }
            for hit in results[0]
        ]
    
    async def delete(self, ids: List[str]) -> bool:
        """Delete from Milvus"""
        collection = self.Collection("documents")
        collection.delete(f"id in {ids}")
        return True


class WeaviateStore(VectorStore):
    """Weaviate vector store implementation"""
    
    def __init__(self):
        self.config = get_config()
        try:
            import weaviate
            self.client = weaviate.Client(self.config.weaviate_url)
            logger.info("Connected to Weaviate")
        except Exception as e:
            logger.error(f"Weaviate connection error: {e}")
            raise
    
    async def add(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """Add texts to Weaviate"""
        from app.core.llm_client import get_llm_client
        
        llm = get_llm_client()
        ids = []
        
        for text, metadata in zip(texts, metadatas):
            embedding = await llm.embed(text)
            
            obj = {
                "text": text,
                "metadata": metadata
            }
            
            id = self.client.data_object.create(
                obj,
                "Document",
                vector=embedding
            )
            ids.append(id)
        
        logger.info(f"Added {len(ids)} documents to Weaviate")
        return ids
    
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search Weaviate"""
        from app.core.llm_client import get_llm_client
        
        llm = get_llm_client()
        query_embedding = await llm.embed(query)
        
        results = self.client.query.get(
            "Document",
            ["text", "metadata", "_additional {distance}"]
        ).with_near_vector(
            {"vector": query_embedding}
        ).with_limit(k).do()
        
        return [
            {
                "text": obj["text"],
                "metadata": obj["metadata"],
                "distance": obj["_additional"]["distance"]
            }
            for obj in results.get("data", {}).get("Get", {}).get("Document", [])
        ]
    
    async def delete(self, ids: List[str]) -> bool:
        """Delete from Weaviate"""
        for id in ids:
            self.client.data_object.delete(id, "Document")
        return True


class PineconeStore(VectorStore):
    """Pinecone vector store implementation"""
    
    def __init__(self):
        self.config = get_config()
        try:
            import pinecone
            pinecone.init(api_key=self.config.pinecone_api_key)
            self.index = pinecone.Index(self.config.pinecone_index)
            logger.info("Connected to Pinecone")
        except Exception as e:
            logger.error(f"Pinecone connection error: {e}")
            raise
    
    async def add(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """Add texts to Pinecone"""
        from app.core.llm_client import get_llm_client
        import uuid
        
        llm = get_llm_client()
        vectors = []
        
        for text, metadata in zip(texts, metadatas):
            embedding = await llm.embed(text)
            id = str(uuid.uuid4())
            vectors.append((id, embedding, {"text": text, **metadata}))
        
        self.index.upsert(vectors=vectors)
        logger.info(f"Added {len(vectors)} documents to Pinecone")
        
        return [v[0] for v in vectors]
    
    async def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search Pinecone"""
        from app.core.llm_client import get_llm_client
        
        llm = get_llm_client()
        query_embedding = await llm.embed(query)
        
        results = self.index.query(query_embedding, top_k=k, include_metadata=True)
        
        return [
            {
                "text": match["metadata"].get("text"),
                "metadata": {k: v for k, v in match["metadata"].items() if k != "text"},
                "distance": 1 - match["score"]  # Convert similarity to distance
            }
            for match in results["matches"]
        ]
    
    async def delete(self, ids: List[str]) -> bool:
        """Delete from Pinecone"""
        self.index.delete(ids=ids)
        return True


def get_vector_store() -> VectorStore:
    """Get vector store instance"""
    config = get_config()
    
    if config.vector_db_type == "milvus":
        return MilvusStore()
    elif config.vector_db_type == "weaviate":
        return WeaviateStore()
    elif config.vector_db_type == "pinecone":
        return PineconeStore()
    else:
        raise ValueError(f"Unknown vector DB type: {config.vector_db_type}")
