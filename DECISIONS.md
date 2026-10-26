# SocraCode Design Decisions Log

This document records architectural, algorithmic, and design decisions made throughout the project.
Format: `YYYY-MM-DD | Decision | Reason`

- 2026-10-25 | Pluggable runner architecture with local subprocess runner and Docker runner | Local Windows host does not have Docker in PATH; a clean `BaseRunner` abstraction allows immediate local development while preserving containerized sandbox deployment.
- 2026-10-25 | Dedicated Python virtual environment in `backend/.venv` | Isolates backend dependencies (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`) from system Python.
- 2026-10-25 | Strict 5-second execution timeout and process tree termination | Protects runner against infinite loops and fork/runaway execution without hanging the server.
- 2026-10-25 | Pure CSS custom properties for theming (light/dark/system) | Adheres strictly to Section 9.2 design tokens without ad-hoc utility classes or unapproved UI frameworks.
- 2026-10-25 | Monaco Editor with lazy-loading and dynamic theme binding | Provides industry-standard code editing experience matching VS Code, syncing with the SocraCode design tokens.
- 2026-10-25 | Standardized 8 canonical bug categories in `backend/app/categories.py` | Guarantees consistency between backend diagnosis, hint templates, and dashboard concept tracking across all supported languages.
- 2026-10-25 | Synthetic AST and regex bug injection over clean algorithm seed corpus | Fulfills non-negotiable constraint of zero pre-trained weights by establishing a self-sufficient training pipeline.
- 2026-10-26 | Backend Level Gate with SQLite attempt tracking | Enforces non-negotiable constraint 4: clients cannot jump levels, and attempts are persisted with sequential unlocking.
- 2026-10-26 | Hybrid syntax parsing using ast.parse and regex traceback extraction | Provides exact line and column numbers for syntax errors while robustly extracting deepest user frame for runtime exceptions.
- 2026-10-26 | Strict template leak check preventing code fixes in Levels 1 to 3 | Guarantees non-negotiable constraint 3 and proposal evaluation criteria: levels 1–3 contain zero code solutions.
