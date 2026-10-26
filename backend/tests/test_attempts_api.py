import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_attempt_and_hint_lifecycle():
    # 1. Create Attempt for failing code
    payload = {
        "language": "python",
        "source": "web",
        "code": "def check_even(n)\n    return n % 2 == 0",
        "error_text": "SyntaxError: expected ':'",
        "timed_out": False,
    }
    response = client.post("/attempts", json=payload)
    assert response.status_code == 201
    data = response.json()
    attempt_id = data["id"]
    assert data["category"] == "syntax_error"
    assert data["buggy_line"] == 1
    assert data["current_level"] == 0

    # 2. Unlock Level 1 (Nudge)
    hint1_resp = client.post(f"/attempts/{attempt_id}/hint")
    assert hint1_resp.status_code == 200
    h1 = hint1_resp.json()
    assert h1["level"] == 1
    assert h1["level_name"] == "Nudge"
    assert "?" in h1["text"]
    hint_id = h1["hint_id"]

    # 3. Provide feedback on hint 1
    fb_resp = client.post(f"/hints/{hint_id}/feedback", json={"helpful": True})
    assert fb_resp.status_code == 200
    assert fb_resp.json()["helpful"] is True

    # 4. Unlock Level 2 (Concept)
    hint2_resp = client.post(f"/attempts/{attempt_id}/hint")
    assert hint2_resp.status_code == 200
    h2 = hint2_resp.json()
    assert h2["level"] == 2
    assert h2["level_name"] == "Concept"

    # 5. Unlock Level 3 (Location)
    hint3_resp = client.post(f"/attempts/{attempt_id}/hint")
    assert hint3_resp.status_code == 200
    h3 = hint3_resp.json()
    assert h3["level"] == 3
    assert h3["level_name"] == "Location"
    assert "line 1" in h3["text"]
    assert h3["is_last_available_level"] is True

    # 6. Try to unlock beyond max -> 400 Bad Request
    hint4_resp = client.post(f"/attempts/{attempt_id}/hint")
    assert hint4_resp.status_code == 400

    # 7. Resolve attempt
    resolve_resp = client.post(
        f"/attempts/{attempt_id}/resolve",
        json={"reflection": "Forgot the colon at the end of the def statement."},
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"
