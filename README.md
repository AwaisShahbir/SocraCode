# SocraCode: Socratic AI Debugging Tutor

SocraCode is an educational AI tutor for beginner programmers learning **Python, Java, and C++**. Instead of handing over completed fixes, SocraCode delivers graded hints through a strict **five-level hint ladder**, guiding students to diagnose their own bugs and master programming concepts.

---

## Key Features

- **Five-Level Hint Ladder**:
  1. *Nudge*: A targeted guiding question to prompt code re-reading.
  2. *Concept*: Identifies the underlying computer science concept (e.g., off-by-one, variable scope).
  3. *Location*: Narrows down the bug to a specific line or code block.
  4. *Similar Example*: A worked, non-identical example illustrating the fix pattern.
  5. *Full Solution*: Unlocks only on deliberate confirmation with comprehensive reasoning (never guessed).
- **Backend-Enforced Level Gate**: Clients cannot skip levels; hints unlock sequentially.
- **Dual Client Support**: React web portal (with Monaco editor) and VS Code extension.
- **Two Operating Modes**:
  - *Instructor Mode*: Course assignments with hidden reference solutions and class struggle dashboards.
  - *Free-Practice Mode*: Independent coding with personal diagnostic history and concept tracking.
- **Zero External AI Services**: No LLM API calls; all diagnosis is performed by custom models, rule systems, and syntax parsers trained from scratch.
- **Sandboxed Execution**: Isolated runner with strict CPU, memory, and execution timeouts.

---

## Repository Structure

```text
socraCode/
├── backend/          # FastAPI REST API, runner, parser, rules, and hint engine
│   ├── app/
│   └── tests/
├── web/              # React + TypeScript + Vite web portal
│   └── src/
├── ml/               # Bug injection dataset generator, model training, evaluation
│   ├── data/
│   └── scripts/
├── docs/             # Architecture, API contracts, datasets, HCI evaluation
├── sandbox/          # Docker sandbox specifications
├── DECISIONS.md      # Architecture and design decision log
└── CHANGELOG.md      # Chronological release log
```

---

## Quickstart (Step 1)

### 1. Backend Setup
```bash
# Navigate to backend
cd backend

# Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
Server runs at `http://127.0.0.1:8000`. Swagger API docs available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
# Navigate to web portal
cd web

# Install dependencies and start Vite dev server
npm install
npm run dev
```
Web app runs at `http://localhost:5173`.
