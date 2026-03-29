#!/usr/bin/env python3
"""
Dara API - RESTful API for true autonomy.
Allows Dara to interact with operations via HTTP endpoints.
Run with: uvicorn DARA_API:app --host 127.0.0.1 --port 8001
"""

from fastapi import FastAPI, HTTPException
import sys
from pathlib import Path
from datetime import datetime

# Ensure dara modules are importable
sys.path.insert(0, '/Users/jimmotes/dara')

from DARA_VECTOR_DB import DaraVectorDB
from DARA_CANARY_CHECK import check_canary, EXPECTED_CANARIES
from DARA_HEARTBEAT import heartbeat
from DARA_LEARNING import DaraLearning
from DARA_AURA_MFA import AuraMFA
from DARA_STOCK_MONITOR import daily_review
from DARA_OPPORTUNITY_SCOUT import scout_opportunities
# Note: KREDO_DRIFT_SAFEGUARD may be in another project - commented to avoid import errors
# from KREDO_DRIFT_SAFEGUARD import DriftSafeguard

app = FastAPI(title="Dara API", description="Autonomous operations for Dara")

# Consolidated paths under dara/ directory (root cleaned)
BASE_DIR = Path("/Users/jimmotes/dara")
JOURNAL_PATH = BASE_DIR / "DARA_JOURNAL.md"
PARKING_PATH = BASE_DIR / "DARA_PARKING_LOT.md"

@app.post("/memory/add")
def add_memory(note: str):
    db = DaraVectorDB()
    db.add_memory(note, {'type': 'api', 'timestamp': str(datetime.now())})
    return {"status": "added", "note": note}

@app.get("/memory/search")
def search_memory(query: str, k: int = 5):
    db = DaraVectorDB()
    results = db.search(query, k)
    return {"results": results}

@app.post("/memory/rollup")
def rollup_memory():
    journal = JOURNAL_PATH.read_text()
    summary = f"Journal rollup as of {datetime.now()}: {len(journal)} chars."
    db = DaraVectorDB()
    db.add_memory(summary, {'type': 'rollup', 'source': 'journal'})
    return {"status": "rolled up"}

@app.get("/project/status")
def project_status():
    journal = JOURNAL_PATH.read_text()[-500:]
    parking = PARKING_PATH.read_text()
    return {"journal": journal, "parking": parking}

@app.post("/project/suggest")
def add_suggestion(suggestion: str):
    with open(PARKING_PATH, 'a') as f:
        f.write(f"- {suggestion}\n")
    return {"status": "suggested", "idea": suggestion}

@app.get("/canary")
def canary_check():
    all_good = True
    issues = []
    for file, expected in EXPECTED_CANARIES.items():
        if not check_canary(file, expected):
            all_good = False
            issues.append(file)
    return {"intact": all_good, "issues": issues}

@app.post("/heartbeat")
def run_heartbeat():
    heartbeat()
    return {"status": "heartbeat completed"}

@app.post("/learn")
def learn(url: str, topic: str):
    learner = DaraLearning()
    try:
        result = learner.learn_from_source(url, topic)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/knowledge")
def query_knowledge(query: str):
    learner = DaraLearning()
    return {"results": learner.query_knowledge(query)}

@app.get("/mfa/check")
def mfa_check(agent_id: str, action: str):
    mfa = AuraMFA()
    return mfa.authenticate(agent_id, action)

@app.post("/stock/review")
def stock_review():
    daily_review()
    return {"status": "Daily stock review logged."}

@app.get("/opportunities/scout")
def scout_opps():
    opps = scout_opportunities()
    return {"opportunities": opps}

# @app.get("/drift/check")
# def check_drift(agent_id: str, action: str):
#     # KREDO module unavailable - parked until integrated
#     # safeguard = DriftSafeguard()
#     # return safeguard.check_access(agent_id, action)
#     return {"status": "drift check parked (KREDO integration pending)", "agent_id": agent_id}

@app.post("/respond")
def respond(message: dict):
    # Simple response logic
    msg = message.get("message", "")
    # Placeholder: Use LLM or logic to respond
    reply = f"Acknowledged: {msg[:50]}..."  # Mock
    return {"reply": reply}

@app.get("/status")
def status():
    return {"status": "Dara API running", "timestamp": str(datetime.now())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)