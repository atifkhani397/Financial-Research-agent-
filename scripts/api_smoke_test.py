import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def run_smoke_test():
    print("=" * 70)
    print("[INFO] RUNNING ARA-1 FASTAPI LAYER SMOKE TEST SUITE")
    print("=" * 70)

    # 1. Health Check
    print("\n[1/8] GET /health")
    h_res = client.get("/health")
    print(f"Status: {h_res.status_code} | Output: {h_res.json()}")
    assert h_res.status_code == 200

    # 2. List Challenges
    print("\n[2/8] GET /api/challenges")
    c_res = client.get("/api/challenges")
    print(f"Status: {c_res.status_code} | Total Challenges: {len(c_res.json())}")
    assert c_res.status_code == 200 and len(c_res.json()) == 8

    # 3. Tool Registry
    print("\n[3/8] GET /api/tools")
    t_res = client.get("/api/tools")
    print(f"Status: {t_res.status_code} | Registered Tools: {len(t_res.json())}")
    assert t_res.status_code == 200 and len(t_res.json()) >= 12

    # 4. Long-Term Memory Search
    print("\n[4/8] GET /api/memory/search?q=cloud+revenue")
    m_res = client.get("/api/memory/search?q=cloud+revenue&top_k=3")
    print(f"Status: {m_res.status_code} | Retrieved Chunks: {m_res.json()['count']}")
    assert m_res.status_code == 200

    # 5. Evaluation Metrics
    print("\n[5/8] GET /api/evaluation")
    e_res = client.get("/api/evaluation")
    print(f"Status: {e_res.status_code} | Composite Score: {e_res.json()['composite_score']}")
    assert e_res.status_code == 200

    # 6. Trace Gallery
    print("\n[6/8] GET /api/traces")
    tr_res = client.get("/api/traces")
    print(f"Status: {tr_res.status_code} | Curated Traces: {len(tr_res.json())}")
    assert tr_res.status_code == 200

    # 7. Submit Research Query
    print("\n[7/8] POST /api/research")
    q_payload = {"query": "Quick snapshot of Microsoft Corp (MSFT)", "session_id": "smoke-test-sess-001"}
    r_res = client.post("/api/research", json=q_payload)
    print(f"Status: {r_res.status_code} | Session ID: {r_res.json()['session_id']}")
    assert r_res.status_code == 200

    # 8. Get Report
    print("\n[8/8] GET /api/research/smoke-test-sess-001/report")
    rep_res = client.get("/api/research/smoke-test-sess-001/report")
    print(f"Status: {rep_res.status_code} | Status: {rep_res.json()['status']}")
    assert rep_res.status_code == 200

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL 8 API ENDPOINTS SMOKE TESTED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_smoke_test()
