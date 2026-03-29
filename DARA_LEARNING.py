#!/usr/bin/env python3
"""
Dara Learning Module - Secure growth and knowledge expansion.
Allows Dara to learn from curated sources, with safety checks.
"""

import requests
from pathlib import Path
from datetime import datetime
from DARA_VECTOR_DB import DaraVectorDB
from DARA_CANARY_CHECK import check_canary, EXPECTED_CANARIES

class DaraLearning:
    def __init__(self):
        self.db = DaraVectorDB()
        self.safe_domains = ['moltbook.com', 'github.com', 'arxiv.org', 'wikipedia.org']  # Whitelist

    def learn_from_source(self, url: str, topic: str):
        # Security check: Only safe domains
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if domain not in self.safe_domains:
            raise ValueError(f"Unsafe domain: {domain}")

        # Fetch content (limit size)
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Fetch failed: {response.status_code}")

        content = response.text[:5000]  # Limit to 5k chars
        summary = f"Learned from {url} on {topic}: {content[:200]}..."

        # Store in vector DB
        self.db.add_memory(summary, {'type': 'learning', 'source': url, 'topic': topic})

        # Log to journal
        journal_path = Path("/Users/jimmotes/DARA_JOURNAL.md")
        with open(journal_path, 'a') as f:
            f.write(f"\n## Learning {datetime.now()}\n- Topic: {topic}\n- Source: {url}\n- Stored in memory.\n")

        return {"status": "learned", "summary": summary}

    def query_knowledge(self, query: str):
        results = self.db.search(query, k=3)
        return results

# Example usage
if __name__ == "__main__":
    learner = DaraLearning()
    # learner.learn_from_source("https://en.wikipedia.org/wiki/Artificial_intelligence", "AI basics")
    print(learner.query_knowledge("AI"))