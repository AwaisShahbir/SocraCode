# SocraCode REST API Specification

Base URL: `http://127.0.0.1:8000`

---

## 1. System Endpoints

### `GET /health`
Returns system and runner operational status.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "runner": "local",
  "languages_supported": ["python"]
}
```

---

## 2. Code Execution (Web Portal)

### `POST /runs`
Compiles/interprets student code in an isolated environment with resource and execution timeouts.

**Request Body**:
```json
{
  "language": "python",
  "code": "print('Hello, SocraCode!')",
  "stdin": null
}
```

**Response `200 OK`**:
```json
{
  "stdout": "Hello, SocraCode!\n",
  "stderr": "",
  "exit_code": 0,
  "duration_ms": 42.1,
  "timed_out": false
}
```

**Response `200 OK` (Error / Exception)**:
```json
{
  "stdout": "",
  "stderr": "Traceback (most recent call last):\n  File \"script.py\", line 1, in <module>\n    print(x)\nNameError: name 'x' is not defined\n",
  "exit_code": 1,
  "duration_ms": 38.5,
  "timed_out": false
}
```

**Response `200 OK` (Execution Timeout)**:
```json
{
  "stdout": "",
  "stderr": "Execution timed out after 5.0 seconds. Possible infinite loop detected.",
  "exit_code": -1,
  "duration_ms": 5002.3,
  "timed_out": true
}
```

---

## 3. Hint Ladder & Attempts (Weeks 3+)

### `POST /attempts`
Creates an attempt session tracking a student's struggle with failing code.

### `POST /attempts/{id}/hint`
Unlocks and returns the next permissible hint level (Level 1 -> 5). Enforces that clients cannot jump ahead.

### `POST /attempts/{id}/resolve`
Marks an attempt resolved once the student has fixed their code.

### `GET /me/progress`
Retrieves student mastery statistics by concept.
