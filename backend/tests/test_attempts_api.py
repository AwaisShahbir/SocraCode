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
    assert data["max_level_allowed"] == 5

    # 2. Unlock Level 1 (Nudge)
    h1 = client.post(f"/attempts/{attempt_id}/hint").json()
    assert h1["level"] == 1
    assert h1["level_name"] == "Nudge"
    hint_id = h1["hint_id"]

    # 3. Provide feedback on hint 1
    fb_resp = client.post(f"/hints/{hint_id}/feedback", json={"helpful": True})
    assert fb_resp.status_code == 200
    assert fb_resp.json()["helpful"] is True

    # 4. Unlock Level 2 (Concept)
    h2 = client.post(f"/attempts/{attempt_id}/hint").json()
    assert h2["level"] == 2
    assert h2["level_name"] == "Concept"

    # 5. Unlock Level 3 (Location)
    h3 = client.post(f"/attempts/{attempt_id}/hint").json()
    assert h3["level"] == 3
    assert h3["level_name"] == "Location"
    assert "line 1" in h3["text"]

    # 6. Unlock Level 4 (Similar Example)
    h4 = client.post(f"/attempts/{attempt_id}/hint").json()
    assert h4["level"] == 4
    assert h4["level_name"] == "Similar Example"
    assert h4["example_code"] is not None

    # 7. Unlock Level 5 (Full Solution)
    h5 = client.post(f"/attempts/{attempt_id}/hint").json()
    assert h5["level"] == 5
    assert h5["level_name"] == "Full Solution"
    assert h5["solution_code"] is not None
    assert "def check_even(n):" in h5["solution_code"]
    assert h5["is_last_available_level"] is True

    # 8. Try to unlock beyond level 5 -> 400 Bad Request
    beyond = client.post(f"/attempts/{attempt_id}/hint")
    assert beyond.status_code == 400

    # 9. Resolve attempt
    resolve_resp = client.post(
        f"/attempts/{attempt_id}/resolve",
        json={"reflection": "Forgot the colon at the end of the def statement."},
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["status"] == "resolved"
