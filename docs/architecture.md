# SocraCode: Architecture Specification

## 1. System Overview

SocraCode provides pedagogical debugging assistance without revealing immediate code solutions. The architecture decouples client interfaces from analysis engines via a single unified FastAPI backend.

```text
+-----------------------------+       +-------------------------------+
| React Web Portal (Monaco)   |       | VS Code Extension (Webview)   |
+-----------------------------+       +-------------------------------+
               \                             /
                \                           /
                 v                         v
       +---------------------------------------------+
       |           FastAPI Shared REST Backend       |
       |  (Auth, Runner, Parsers, Rules, Classifier) |
       +---------------------------------------------+
               /              |               \
              v               v                v
      +--------------+  +-----------+   +-------------------+
      | Code Sandbox |  | SQLite DB |   | Hint Ladder Engine|
      | (Runner)     |  |           |   | (Templates/Rules) |
      +--------------+  +-----------+   +-------------------+
```

---

## 2. Core Modules

### 2.1 Backend (`backend/app/`)
- `api/`: REST endpoints handling authentication, code execution (`/runs`), attempt lifecycle (`/attempts`), hint progression (`/attempts/{id}/hint`), and analytics.
- `runner/`: Execution environment enforcing strict execution timeouts, memory bounds, and output limits. Uses a pluggable interface (`BaseRunner`) with `SubprocessRunner` (local dev) and `DockerRunner` (production sandbox).
- `parser/`: Parses runtime tracebacks and compiler diagnostics into normalized error records (ErrorType, Message, LineNumber, ColumnNumber).
- `rules/`: Deterministic expert-system checks for common unambiguous mistakes (syntax, undefined variables, missing colons).
- `ml/`: Custom model inference (trained from scratch) predicting bug category and outputting confidence scores.
- `retrieval/`: TF-IDF similarity matcher over a curated catalog of worked examples for Level 4 hints.
- `hints/`: Hint templates, template hydration, and backend level-gate enforcer preventing clients from bypassing lower hint tiers.
- `student_model/`: Tracks struggle frequencies, hints used, and concept recency per user.
- `db/`: SQLite models and repositories for users, attempts, assignments, and hint interactions.

### 2.2 Web Portal (`web/`)
- React + TypeScript + Vite.
- Monaco Editor: Configured with Python syntax rules, line error markers, and theme synchronization.
- Hint Ladder Stepper: Displays the 5 progressive tiers (Nudge, Concept, Location, Example, Full Solution) with strict state gates (`done`, `current`, `locked`).
- Output Console: Real-time stdout, stderr, run time, and execution status.
- Design System: Custom CSS properties adhering to WCAG 2.2 AA contrast standards with Light, Dark, and System modes.

---

## 3. Communication Contract

All communications between interfaces and the backend take place via JSON over HTTP.
- Web runs are processed via server-side sandboxing (`POST /runs`).
- Extension runs execute on the student's local toolchain, submitting only `{ code, error_text, language }` to `POST /attempts`.
- Hint progression is managed via `POST /attempts/{id}/hint`, returning solely the template for the authorized level.
