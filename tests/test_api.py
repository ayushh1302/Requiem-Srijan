import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_upload_and_analyze_flow():
    # 1. Upload sample text contract
    sample_text = """RESIDENTIAL LEASE
    1. Monthly Rent: Tenant pays INR 30000 by 5th.
    2. Eviction: Landlord can evict within 24 hours without notice.
    3. Security Deposit: INR 100000 refundable upon 30 days.
    """
    file_bytes = io.BytesIO(sample_text.encode("utf-8"))
    upload_resp = client.post(
        "/upload",
        files={"file": ("test_lease.txt", file_bytes, "text/plain")},
        data={"session_id": "test_session_123"}
    )
    assert upload_resp.status_code == 200
    up_data = upload_resp.json()
    assert up_data["session_id"] == "test_session_123"

    # 2. Trigger Analysis
    analyze_resp = client.post(
        "/analyze",
        json={"session_id": "test_session_123"}
    )
    assert analyze_resp.status_code == 200
    an_data = analyze_resp.json()
    assert "fairness" in an_data
    assert len(an_data["clauses"]) > 0
    assert len(an_data["analysis"]) > 0

    # 3. Test RAG Chatbot
    chat_resp = client.post(
        "/chat",
        json={"session_id": "test_session_123", "message": "What is the monthly rent?"}
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "answer" in chat_data
    assert len(chat_data["answer"]) > 5

    # 4. Test PDF Report Generation
    report_resp = client.get("/report/test_session_123")
    assert report_resp.status_code == 200
    assert report_resp.headers["content-type"] == "application/pdf"

    # 5. Reset Session
    reset_resp = client.post("/reset/test_session_123")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"
