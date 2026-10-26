# Changelog

All notable changes to SocraCode will be documented in this file.
The format is based on Keep a Changelog.

## [Step 3] - Weeks 6-7: Full Ladder & Classifier - 2026-10-26

### Added
- Feature extraction pipeline (`backend/app/ml/features.py`) extracting token n-grams and AST syntax characteristics without pretrained embeddings.
- Scratch-trained PyTorch multi-layer perceptron neural network (`backend/app/ml/model.py`) for bug category classification.
- Baseline Scikit-learn Random Forest classifier with comparative metrics (`backend/app/ml/baseline.py`).
- Standalone offline training pipeline (`ml/scripts/train.py`) with held-out validation and metrics export (`ml/data/generated/model_metrics.json`).
- Production ML classifier inference service (`backend/app/ml/classifier.py`) with confidence threshold fallback to expert rule engine.
- Parallel worked examples catalog (`backend/app/retrieval/examples_library.py`) covering all 8 bug categories.
- Level 4 TF-IDF cosine similarity example retriever (`backend/app/retrieval/tfidf_matcher.py`) matching student buggy code to parallel worked problems.
- Level 5 deterministic rule-based fix synthesizer (`backend/app/rules/fixer.py`) with AST syntax validation, diff generation, and pedagogical explanations.
- Extended Level Gate (`backend/app/hints/level_gate.py`) supporting full 5-level ladder (Level 4: Worked Example; Level 5: Solution + Explanation).
- Frontend confirmation modal for Level 5 ("Show Full Solution? Keep Trying vs Show Solution") per Section 9.4.
- Frontend Level 4 code block display and Level 5 fix viewer with "Apply Fix to Editor" and copy actions.
- 31 backend unit and integration tests passing (`test_runner`, `test_api`, `test_parser`, `test_rules`, `test_hints`, `test_leak_check`, `test_attempts_api`, `test_retrieval`, `test_fixer`, `test_classifier`).
- End-to-end browser subagent verification of the complete 5-level ladder, fix application, execution, and reflection flow.

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
