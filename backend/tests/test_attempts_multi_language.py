import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_java_attempt_and_full_hint_ladder():
    # Student code with missing semicolon on line 3
    java_code = """public class Solution {
    public static void main(String[] args) {
        int answer = 42
    }
}"""
    stderr = """Solution.java:3: error: ';' expected
        int answer = 42
                       ^
1 error"""

    # 1. Create Attempt for Java
    res = client.post(
        "/attempts",
        json={
            "language": "java",
            "source": "web",
            "code": java_code,
            "error_text": stderr,
            "timed_out": False,
        },
    )
    assert res.status_code == 201
    data = res.json()
    attempt_id = data["id"]
    assert data["language"] == "java"
    assert data["category"] == "syntax_error"
    assert data["buggy_line"] == 3

    # 2. Level 1: Nudge
    h1 = client.post(f"/attempts/{attempt_id}/hint")
    assert h1.status_code == 200
    h1_data = h1.json()
    assert h1_data["level"] == 1
    assert "Take a close look at the punctuation" in h1_data["text"]

    # 3. Level 2: Concept
    h2 = client.post(f"/attempts/{attempt_id}/hint")
    assert h2.status_code == 200
    h2_data = h2.json()
    assert h2_data["level"] == 2
    assert "Syntax error related to Java's grammar" in h2_data["text"]

    # 4. Level 3: Location
    h3 = client.post(f"/attempts/{attempt_id}/hint")
    assert h3.status_code == 200
    h3_data = h3.json()
    assert h3_data["level"] == 3
    assert "line 3" in h3_data["text"]

    # 5. Level 4: Worked Example (Java)
    h4 = client.post(f"/attempts/{attempt_id}/hint")
    assert h4.status_code == 200
    h4_data = h4.json()
    assert h4_data["level"] == 4
    assert h4_data["example_code"] is not None
    assert "public class" in h4_data["example_code"]

    # 6. Level 5: Full Solution (Deterministic fix)
    h5 = client.post(f"/attempts/{attempt_id}/hint")
    assert h5.status_code == 200
    h5_data = h5.json()
    assert h5_data["level"] == 5
    assert h5_data["solution_code"] is not None
    assert "int answer = 42;" in h5_data["solution_code"]
    assert "Added missing semicolon" in h5_data["explanation"]


def test_cpp_attempt_and_full_hint_ladder():
    # Student code with missing semicolon on line 4
    cpp_code = """#include <iostream>
int main() {
    int total = 100
    return 0;
}"""
    stderr = """solution.cpp:4:5: error: expected ';' before 'return'
    return 0;
    ^~~~~~"""

    # 1. Create Attempt for C++
    res = client.post(
        "/attempts",
        json={
            "language": "cpp",
            "source": "web",
            "code": cpp_code,
            "error_text": stderr,
            "timed_out": False,
        },
    )
    assert res.status_code == 201
    data = res.json()
    attempt_id = data["id"]
    assert data["language"] == "cpp"
    assert data["category"] == "syntax_error"

    # 2. Unlock hints up to Level 4
    client.post(f"/attempts/{attempt_id}/hint") # L1
    client.post(f"/attempts/{attempt_id}/hint") # L2
    client.post(f"/attempts/{attempt_id}/hint") # L3
    h4 = client.post(f"/attempts/{attempt_id}/hint") # L4
    assert h4.status_code == 200
    assert h4.json()["level"] == 4
    assert h4.json()["example_code"] is not None
    assert "#include" in h4.json()["example_code"]

    # 3. Level 5 Fix
    h5 = client.post(f"/attempts/{attempt_id}/hint") # L5
    assert h5.status_code == 200
    assert h5.json()["level"] == 5
    assert h5.json()["solution_code"] is not None
    assert "int total = 100;" in h5.json()["solution_code"]
