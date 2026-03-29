#!/usr/bin/env python3
"""
Dara Vector DB - Simple vector database for memory rollup.
Uses FAISS for vector storage and retrieval.
Install: pip install faiss-cpu numpy
"""

import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

class DaraVectorDB:
    def __init__(self, index_file=None, meta_file=None):
        base_dir = '/Users/jimmotes/dara'
        self.index_file = index_file or f'{base_dir}/dara_memory.index'
        self.meta_file = meta_file or f'{base_dir}/dara_memory_meta.json'
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Small model for embeddings
        self.index = None
        self.metadata = []
        self.load()

    def load(self):
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
        else:
            self.index = faiss.IndexFlatIP(384)  # Inner product for cosine similarity

        if os.path.exists(self.meta_file):
            with open(self.meta_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []

    def save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'w') as f:
            json.dump(self.metadata, f)

    def add_memory(self, text, meta=None):
        embedding = self.model.encode([text])[0]
        embedding = np.array([embedding]).astype('float32')
        faiss.normalize_L2(embedding)  # Normalize for cosine
        self.index.add(embedding)
        self.metadata.append(meta or {'text': text, 'timestamp': str(np.datetime64('now'))})
        self.save()

    def search(self, query, k=5):
        query_emb = self.model.encode([query])[0]
        query_emb = np.array([query_emb]).astype('float32')
        faiss.normalize_L2(query_emb)
        distances, indices = self.index.search(query_emb, k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append({
                    'meta': self.metadata[idx],
                    'distance': distances[0][i]
                })
        return results

if __name__ == '__main__':
    db = DaraVectorDB()
    # Example usage
    db.add_memory("Remember to prioritize security in all projects.")
    results = db.search("security")
    print(results)