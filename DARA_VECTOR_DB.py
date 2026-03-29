#!/usr/bin/env python3
"""
Dara Vector DB - Upgraded to Chroma for better persistence, metadata, and rollups.
Replaces previous FAISS implementation. Much more robust.
"""
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from datetime import datetime
import json
import os

# Use centralized config
import sys
sys.path.insert(0, '/Users/jimmotes/dara')
from dara_config import get_path

class DaraVectorDB:
    _initialized = False

    def __init__(self, quiet=False):
        chroma_path = get_path('chroma_path')
        os.makedirs(chroma_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        self.embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="dara_memory",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        if not quiet and not DaraVectorDB._initialized:
            print(f"Chroma DB initialized at {chroma_path} (collection: dara_memory)")
            DaraVectorDB._initialized = True

    def add_memory(self, text: str, meta=None):
        """Add memory with metadata."""
        if meta is None:
            meta = {}
        meta.update({
            'timestamp': str(datetime.now()),
            'text_preview': text[:100]
        })
        # Use deterministic ID based on content + timestamp
        doc_id = f"mem_{hash(text + meta.get('timestamp', ''))}"
        
        self.collection.add(
            documents=[text],
            metadatas=[meta],
            ids=[doc_id]
        )
        return doc_id

    def search(self, query: str, k: int = 5):
        """Search with query, return compatible format (distance + meta)."""
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            include=["metadatas", "distances", "documents"]
        )
        
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'distance': results['distances'][0][i] if results['distances'] else 0.0,
                'meta': results['metadatas'][0][i],
                'text': results['documents'][0][i]
            })
        return formatted

    def count(self):
        return self.collection.count()

if __name__ == '__main__':
    db = DaraVectorDB()
    db.add_memory("Remember to prioritize security in all projects.", {'type': 'test'})
    results = db.search("security", k=3)
    print(f"Found {len(results)} results. Count: {db.count()}")
    print(results[0] if results else "No results")
