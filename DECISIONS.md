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
