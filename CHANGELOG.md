# Changelog

All notable changes to SocraCode will be documented in this file.
The format is based on Keep a Changelog.

## [Step 1] - Weeks 1-2: Learn and Design (Scaffolding & Python Runner) - 2026-10-25

### Added
- Repository scaffold: `backend/`, `web/`, `docs/`, `ml/`, `sandbox/`.
- System architecture specification (`docs/architecture.md`).
- REST API contracts (`docs/api.md`) including `/health` and `/runs`.
- Dataset and bug category taxonomy documentation (`docs/datasets.md`).
- Backend FastAPI app with health and code execution endpoints.
- Pluggable code execution engine with local isolated subprocess runner (timeout enforcement, output capture).
- Python unit tests for runner and API endpoints using pytest.
- Web front-end scaffold using React + TypeScript + Vite.
- Custom CSS design system implementing all Section 9.2 design tokens with light/dark/system theme support.
- Monaco Editor integration for Python with auto theme synchronization.
- Output & terminal console with stdout/stderr segregation and run duration metrics.
- Keyboard shortcut `Ctrl/Cmd + Enter` to run code.
- Initial bug generator script prototype (`ml/scripts/generate_bugs.py`) for bug injection.
