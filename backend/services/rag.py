import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any
from backend.utils.nim_client import nim_client
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.index = None
        self.documents = [] # Metadata store
        self.index_file = "rag_index.faiss"
        self.docs_file = "rag_docs.pkl"
        self.dimension = 1024 # Depends on embedding model
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_file) and os.path.exists(self.docs_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.docs_file, 'rb') as f:
                self.documents = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

    def _save_index(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.docs_file, 'wb') as f:
            pickle.dump(self.documents, f)

    async def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        if not texts:
            return

        try:
            embeddings = await nim_client.embed("nvidia/nv-embed-qa-4", texts)
            
            # Ensure dimension matches
            if len(embeddings[0]) != self.dimension:
                # Re-init index if dimension mismatch (simple handling)
                self.dimension = len(embeddings[0])
                self.index = faiss.IndexFlatL2(self.dimension)

            vectors = np.array(embeddings).astype('float32')
            self.index.add(vectors)
            self.documents.extend(metadatas)
            self._save_index()
            logger.info(f"Added {len(texts)} documents to RAG index.")
        except Exception as e:
            logger.error(f"Failed to add documents to RAG: {e}")

    async def query(self, query_text: str, k: int = 3) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []

        try:
            embeddings = await nim_client.embed("nvidia/nv-embed-qa-4", [query_text])
            vector = np.array(embeddings).astype('float32')
            
            distances, indices = self.index.search(vector, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.documents):
                    doc = self.documents[idx]
                    doc['score'] = float(distances[0][i])
                    results.append(doc)
            
            return results
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return []

rag_service = RAGService()
