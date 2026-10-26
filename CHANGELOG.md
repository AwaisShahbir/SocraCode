# Changelog

All notable changes to SocraCode will be documented in this file.
The format is based on Keep a Changelog.

## [Step 2] - Weeks 3-5: Python Engine & Core Hints (Levels 1 to 3) - 2026-10-26

### Added
- Python error parser (`backend/app/parser/python_parser.py`) for syntax errors, tracebacks, and heuristic line localization.
- Expert rule engine (`backend/app/rules/python_rules.py`) detecting the 8 bug categories and generating pedagogical context.
- SQLite database schema and repository (`backend/app/db/`) for attempt sessions and hint event persistence.
- Socratic hint templates for Python Levels 1-3 (`backend/app/hints/templates.py`) strictly avoiding code fix leaks.
- Backend Level Gate (`backend/app/hints/level_gate.py`) enforcing sequential hint unlocking (1 -> 2 -> 3) and template hydration.
- REST API endpoints (`backend/app/api/routes_attempts.py`) for `/attempts`, `/attempts/{id}/hint`, `/attempts/{id}/resolve`, and `/hints/{id}/feedback`.
- Automated leak check tests verifying that Levels 1 to 3 contain zero code fixes or solution keywords.
- Interactive Hint Ladder UI panel (`web/src/features/ladder/HintLadderPanel.tsx`) with collapsible history, thumbs up/down feedback, and line highlight buttons.
- Monaco Editor line inspection and navigation integration for Level 3 Location hints.
- Reflection dialog prompted upon successful bug resolution.
- 23 unit and integration tests passing in backend pytest suite.

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
