# SocraCode: Master Project Prompt

Paste this whole file into your AI code editor as the first message, or save it in the repo root as `CLAUDE.md` / `.cursorrules` / `PROJECT_CONTEXT.md` so the editor reads it every session.

---

## 0. How you (the editor) must use this prompt

You are the lead engineer and UI designer on a semester project called **SocraCode**. This document is the single source of truth for the whole project. It describes everything we will build, but **we will build it step by step across about 16 weeks**.

Rules for this first message:

1. **Do not write any code yet.** Read everything, then reply with: (a) a summary of the project in at most 10 bullets, (b) any contradictions or gaps you found, (c) up to 8 numbered questions you need answered before Step 1, (d) a proposed repository layout. Then wait.
2. In every later message I will tell you which step to do. Do only that step. Do not build ahead.
3. Before writing code for a step, give a short plan (files to create or change, and why). After the code, give: how to run it, how to test it, and what is left.
4. If something in a later instruction conflicts with this document, point out the conflict and ask. Do not silently change the design.
5. Keep a `DECISIONS.md` file. Every time we make a design choice, add one line: date, decision, reason.

---

## 1. What SocraCode is

SocraCode is an AI-assisted **Socratic debugging tutor**. When a student's program fails, it does not hand over the fixed code. It gives **graded hints in five levels**, so the student finds the bug themselves and learns the concept behind it.

It has **one shared backend and two interfaces**:

- **Web portal** (React): code editor, run, hint ladder, personal dashboard, and instructor views.
- **VS Code extension** (TypeScript): a "Help me" command and a sidebar hint panel, using the same backend.

It supports **two ways of using it**:

- **With an instructor:** the instructor creates assignments (with a hidden reference solution), and sees a class dashboard.
- **Without an instructor (free practice):** a student writes or pastes any program, gets hints and a personal dashboard. No class, assignment or reference solution is needed.

Languages, in this order: **Python first, then Java, then C++**. Do not start a new language until the previous one works end to end.

---

## 2. Non-negotiable constraints

These are the hard rules. If a request would break one, stop and tell me.

1. **No external AI service.** No OpenAI, Anthropic, Gemini, Hugging Face Inference or any other LLM API. No calls to the internet at runtime for intelligence.
2. **No pretrained models or pretrained weights.** The classifier is trained from scratch by us on our own generated data. A scikit-learn baseline is allowed for comparison.
3. **Hints come from templates**, selected by rules and the classifier. The model chooses which template to use. **It never generates free text.**
4. **The level gate is enforced on the backend.** The client can never skip a level. Both the web app and the extension obey the same rule.
5. **Never guess a fix.** Level 5 (full solution) comes only from (a) the instructor's reference solution, or (b) a rule-based fix for a bug category the rule base can fix with certainty. If neither exists, the ladder stops at level 4 and the interface says so honestly.
6. **Reference solutions never leave the server.** They are never sent to a browser or the extension.
7. **Student code runs in a sandbox** on the server for the web app (see section 8). The extension runs code on the student's own machine and sends only the code and error text to the backend.
8. **Confidence fallback.** If classifier confidence is low, the engine falls back to a generic level 1 guiding question instead of guessing a category.
9. **Add no new dependency without asking me first.** Say what it is, why, and what the alternative is.

---

## 3. Architecture

```
React web app (browser) ──┐
                          ├──> FastAPI backend ──> Runner/Parser ──> Rules + ML classifier ──> Level gate + Hint builder
VS Code extension ────────┘            │                                                              │
                                       └──────────────> SQLite <──────────────────────────────────────┘
                                                           │
                                          Dashboard data + Instructor views
```

### 3.1 Backend modules (Python 3.11+, FastAPI)

| Module | Job |
|--------|-----|
| `api/` | REST endpoints, auth, validation (Pydantic), rate limiting |
| `runner/` | Compile and run code in a sandbox per language; capture stdout, stderr, exit code, time; enforce limits |
| `parser/` | Turn compiler and interpreter output into structured error objects (type, message, line, column); use `ast` for Python, tree-sitter for Java and C++ |
| `rules/` | If-then expert rules for clear-cut bugs (syntax, undefined name, missing return, and so on) |
| `ml/` | Feature extraction, dataset generator (bug injection), classifier trained from scratch, scikit-learn baseline, evaluation scripts |
| `retrieval/` | TF-IDF similarity over a library of worked examples, used for level 4 |
| `hints/` | Hint templates (per level, bug category and language), the level gate, the hint builder |
| `student_model/` | Counts and recency of concepts per student; feeds the dashboard |
| `db/` | SQLite models and migrations |

### 3.2 Proposed API (confirm before building)

```
POST /auth/register          POST /auth/login          GET /me
POST /runs                   run code in the sandbox (web app only)
POST /attempts               start an attempt: code, language, run result, source (web|extension), optional assignment_id
POST /attempts/{id}/hint     return the NEXT hint level (backend decides which level)
POST /attempts/{id}/resolve  mark fixed; optional reflection text
GET  /me/progress            personal dashboard data
POST /hints/{id}/feedback    helpful / not helpful
-- instructor only --
POST/GET /assignments        create and list (reference solution stored server-side only)
GET  /classes/{id}/dashboard class results
GET  /classes/{id}/export    CSV export
```

### 3.3 Data model (SQLite, first draft)

- `users` (id, name, email, password_hash, role: student | instructor, created_at)
- `classes`, `enrollments`
- `assignments` (id, class_id, title, language, description, starter_code, reference_solution **server-only**, constraints, max_level_allowed)
- `attempts` (id, user_id, assignment_id **nullable**, language, source: web | extension, category, concept, confidence, started_at, resolved_at)
- `hint_events` (id, attempt_id, level, template_id, shown_at, helpful nullable)
- `concept_stats` (user_id, concept, attempts, hints_used, last_seen)

`assignment_id` is nullable because free practice has no assignment.

---

## 4. The engine in detail

### 4.1 Hint ladder (the core product)

| Level | Type | Rule |
|-------|------|------|
| 1 | Guiding question | Makes the student re-read their own code. No code, no names of fixes. |
| 2 | Concept hint | Names the concept (for example off-by-one, scope, missing base case). No code. |
| 3 | Location hint | Narrows to a line or block. No corrected code. |
| 4 | Similar example | A worked example retrieved from our library, **not** the student's exact fix. |
| 5 | Full solution | Only on a deliberate confirmation, and only if allowed by constraint 5. Always includes an explanation. |

Levels unlock **in order**. Level 5 needs an explicit confirm step.

### 4.2 Bug categories (about 8; confirm the final list in Step 1)

Proposed starting list: syntax error, undefined name, type error, index out of range or off-by-one, wrong operator or condition, missing return, loop boundary or infinite loop, wrong variable used. Each category maps to one or more **concepts** shown on the dashboard.

### 4.3 The trained model

- **Data:** thousands of labelled buggy programs generated by **inserting known bugs** into correct programs. Each inserted bug has a known category and line. Keep a smaller hand-written set from course-style exercises **aside for testing only**.
- **Model:** a small neural network trained from scratch (PyTorch or NumPy), with a scikit-learn baseline (logistic regression or random forest) on the same data for comparison.
- **Features:** error type and message tokens, AST or token-level features, code statistics. No pretrained embeddings.
- **Output:** category plus confidence. Below a threshold, fall back to the generic level 1 question.
- **Evaluation scripts** must report accuracy, per-category precision and recall, and a confusion matrix, per language.

### 4.4 Student model

Per student and concept: counts and recency. Used for the dashboard and, later, to suggest which concept to practise.

### 4.5 Automated checks we must be able to report

1. **Diagnosis accuracy** on the held-out set.
2. **Leak rate:** how often levels 1 to 3 contain code or the fix. Target is zero; test it.

---

## 5. User roles and flows

| Role | What they do | What they see |
|------|--------------|---------------|
| Independent student | Free practice: writes any program, asks for hints | Own history and weak concepts. No instructor view. |
| Class student | Opens an assignment, works, asks for hints | Own history plus assignment status |
| Instructor | Creates assignments with a hidden reference solution, reviews the class | Class dashboard, per-student drill-down, CSV export |

Core student flow: write or open code, **Run**, the program fails, **Get hint** (level 1), optionally **Next hint**, fix the bug, **Mark as fixed**, optional reflection ("What was the bug and why did it happen?"), dashboard updates.

---

## 6. Tech stack

| Layer | Choice |
|-------|--------|
| Web front end | React + TypeScript + Vite; Monaco editor; Chart.js or Recharts; accessible headless primitives (for example Radix UI); styling with CSS variables (design tokens); Tailwind only if I approve it |
| Extension | TypeScript, VS Code Extension API, webview sidebar panel |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy or plain SQL with SQLite |
| Code execution | `python`, `javac` and `java`, `g++` inside a sandbox (Docker with CPU, memory, time and no-network limits) |
| Parsing | Python `ast`; tree-sitter for Java and C++ |
| ML | PyTorch or NumPy for our model; scikit-learn for the baseline and TF-IDF |
| Tests | pytest, Vitest, React Testing Library, Playwright for a few end-to-end flows |
| Tooling | Git, ESLint, Prettier, Ruff, mypy or pyright, pre-commit |

---

## 7. Plan (16 weeks). Do only the step I name.

| Weeks | Step | Result |
|-------|------|--------|
| 1-2 | Learn and design: scaffold repo, shared API contract, bug category list, start dataset generator | Editor runs a Python file |
| 3-5 | Python engine and core hints: runner, parser, rules, templates for levels 1 to 3 | Levels 1 to 3 working |
| 6-7 | Full ladder and classifier: levels 4 and 5, ML classifier, SQLite logging, hint panel | Full ladder for Python |
| 8-9 | Java and C++: rules, templates, dataset | Three languages working |
| 10-11 | Dashboard and instructor views; free-practice mode finished | Dashboard ready |
| 12-13 | VS Code extension as a thin client on the same API | Extension works end to end |
| 14-15 | User study with 10 to 15 classmates; fix what it reveals | User study complete |
| 16 | Evaluate, polish, report, demo | Final demo ready |

---

## 8. Security and privacy

- Passwords hashed with argon2 or bcrypt. Sessions via secure, HTTP-only cookies or short-lived tokens.
- Validate every input with Pydantic. Rate-limit run and hint endpoints.
- **Sandbox:** no network, read-only file system except a temp directory, CPU and memory caps, wall-clock timeout, kill on exceed. Test it with deliberately harmful programs (infinite loops, fork bombs, huge allocations, file reads).
- Never log full student code in plain server logs. Store attempts only in the database.
- The extension sends only code and error text. Say this clearly in its settings page.
- CORS locked to our own origin. No secrets in the repo; use `.env` and provide `.env.example`.

---

## 9. GUI and Human-Computer Interaction guide

The interface must feel **professional, calm and trustworthy**. It is a learning tool, so the design goal is to **support productive struggle**: help the student think, never overwhelm them, never shame them.

### 9.1 Design principles (apply and cite them in code comments or `DECISIONS.md` when relevant)

1. **Nielsen's 10 usability heuristics:**
   - *Visibility of system status:* always show whether code is running, a hint is loading, or something has been saved.
   - *Match with the real world:* use plain language ("Get hint"), not system words ("POST attempt").
   - *User control and freedom:* undo, cancel a run, go back to earlier hints at any time.
   - *Consistency and standards:* one name per action everywhere. The button that says "Run" produces a status that says "Running" then "Run finished".
   - *Error prevention:* confirm only where harm is real (level 5, deleting an assignment).
   - *Recognition over recall:* show the level, history and shortcuts on screen.
   - *Flexibility and efficiency:* keyboard shortcuts for experts, with tooltips for beginners.
   - *Aesthetic and minimalist design:* every element earns its place.
   - *Help users recover from errors:* say what happened and how to fix it.
   - *Help and documentation:* short contextual help, not a manual.
2. **Progressive disclosure:** reveal one hint at a time; older hints are collapsed but reachable. Advanced options live in settings.
3. **Hick's law:** few choices at each moment. One clear primary action per screen area (**Get hint**).
4. **Fitts's law:** primary buttons are large and close to where the eyes are; touch targets at least 44 by 44 px (never below 24 by 24, the WCAG 2.2 minimum).
5. **Miller's law and cognitive load:** group related information; keep the hint panel to one idea at a time.
6. **Gestalt principles:** proximity and shared containers for related items, consistent alignment, clear visual hierarchy.
7. **Feedback within 100 ms for clicks, a visible loading state if work takes over 1 second, and a progress indication if it takes over 4 seconds** (for example a compile).
8. **Learning-specific design:** scaffolding (the ladder), a delay-friendly flow (do not push the next hint automatically), metacognition (the reflection prompt), and a non-judgemental tone.
9. **Do not rely on colour alone** to carry meaning. Pair colour with an icon, a label or a pattern.

### 9.2 Design tokens (implement as CSS variables; light and dark share names)

Use semantic names, not raw colours, in components (`--color-surface`, never `#fff`). Starting palette (verify every text pair with a contrast checker; body text needs at least 4.5:1, large text and UI boundaries at least 3:1; adjust values if any pair fails):

| Token | Light | Dark |
|-------|-------|------|
| `--color-bg` | `#F7F8FA` | `#0F1319` |
| `--color-surface` | `#FFFFFF` | `#171C24` |
| `--color-surface-raised` | `#FFFFFF` | `#1E2530` |
| `--color-border` | `#D5D9E0` | `#2E3644` |
| `--color-text` | `#14181F` | `#E8ECF2` |
| `--color-text-muted` | `#4A5260` | `#A3ACBB` |
| `--color-accent` | `#2B5FD9` | `#7AA2FF` |
| `--color-on-accent` | `#FFFFFF` | `#0F1319` |
| `--color-success` | `#1F7A4D` | `#5BD08F` |
| `--color-warning` | `#8A5A00` | `#F0B955` |
| `--color-danger` | `#B3261E` | `#FF8A80` |
| `--color-focus-ring` | `#2B5FD9` | `#9DBBFF` |

Other tokens:

- **Typography:** one UI sans-serif family and one monospace family for code. Suggested: IBM Plex Sans and JetBrains Mono, self-hosted, with system fallbacks. Type scale (px): 12, 14, 16, 20, 24, 32. Body 16 px; code 14 px. Line height 1.5 for body, 1.4 for code. **Line length under 80 characters** for reading text (hint text, explanations).
- **Spacing:** 4 px base grid (4, 8, 12, 16, 24, 32, 48).
- **Radius:** two sizes only: 6 px for controls and 10 px for containers. Do not use one radius on everything.
- **Elevation:** prefer 1 px borders and surface contrast over heavy shadows. Use a shadow only for floating layers (menus, dialogs).
- **Motion:** 120 to 200 ms, ease-out, and **only in response to a user action** (opening, expanding, confirming). No decorative entrance animations, no hover effects on every card. Respect `prefers-reduced-motion` (turn motion off).
- **Icons:** one icon set (for example Lucide), 16 or 20 px, always with a text label or an accessible name.

Avoid the generic "AI-template" look: no gradient washes, no identical rounded cards stacked everywhere, no tracked-out all-caps labels above every heading, no decorative numbering unless the content really is a sequence. Spend visual emphasis in **one** place: the hint ladder. Everything else stays quiet.

### 9.3 Light and dark mode (required)

- Three choices in a theme control: **Light, Dark, System**. Default is **System** (`prefers-color-scheme`). Persist the choice.
- Implement with `data-theme="light|dark"` on `<html>` and CSS variables. A tiny inline script in `index.html` sets the theme **before first paint** to prevent a flash of the wrong theme.
- Every component must be designed and checked in **both** themes. No hard-coded colours.
- The Monaco editor theme must switch with the app theme and use colours that match the tokens. Syntax colours must also meet contrast requirements.
- Charts must read well in both themes (token-based series colours, labelled directly or with a legend, never colour-only).
- Images and icons must work on both backgrounds.
- **VS Code extension:** the webview must **inherit the editor's theme** using VS Code's own CSS variables (`--vscode-editor-background`, `--vscode-foreground`, `--vscode-button-background`, and so on), so it follows light, dark and high-contrast automatically. Do not impose our palette inside VS Code except for small accents.

### 9.4 Layout and key screens

**Practice workspace (main screen)**

```
+----------------------------------------------------------------------------+
| SocraCode      [Language v]   Free practice / Assignment name   [Theme] [Me] |
+-----------------------------------------------+----------------------------+
| Code editor (Monaco)                          | Output | Problems           |
|                                               |  (tabs: stdout / errors)   |
|                                               +----------------------------+
|                                               | Hint ladder                |
| [Run]  [Get hint]            Saved just now   |  1 Question      done      |
+-----------------------------------------------+  2 Concept       current   |
                                                |  3 Location      locked    |
                                                |  4 Example       locked    |
                                                |  5 Full solution locked    |
                                                |  [Get next hint]           |
                                                +----------------------------+
```

- Editor takes about 60 percent of the width; the right column holds output and the ladder. On screens narrower than about 900 px, **stack** them (editor above, panels below, with tabs). Must work down to 360 px wide.
- Left-to-right, top-to-bottom order matches the task order: write, run, read the output, get a hint.

**Hint ladder component (the hero of the product)**

- A vertical stepper with five items. Each item has an icon, a label and a state: *done*, *current*, *locked*.
- **Locked levels are visible but disabled, with the reason** ("Unlocks after level 2"). Never hide them; recognition beats recall.
- Only the current hint is expanded. Earlier hints are collapsed and can be re-opened.
- One primary button: **Get next hint**. After level 4, the button changes to **Show full solution**, which opens a confirmation dialog explaining that trying again first helps learning, with **Keep trying** as the default focus and **Show solution** as the secondary action.
- If level 5 is not available (constraint 5), show a calm, honest message: "SocraCode can't verify a full fix for this bug. Ask your instructor or a classmate." Do not show a disabled mystery button.
- After each hint: a small, optional "Was this hint helpful?" control (thumbs up or down with labels).
- New hint text is announced to screen readers with an `aria-live="polite"` region, and focus is not stolen from the editor.
- After **Mark as fixed**, show an optional reflection box ("What was the bug, and why did it happen?") that can be skipped.

**Student dashboard**

- Top: three plain summary figures (bugs fixed this week, average hints per bug, time to fix) with a short comparison to the previous week in words ("2 fewer hints than last week").
- Middle: **Concepts to practise**, a ranked list with a simple bar and a number, plus a link "Practise this" that opens free practice with a relevant example.
- Below: a recent attempts table (date, language, concept, hints used, time).
- Every chart has a **table view** alternative and direct labels. Never use red-green only.
- Tone: progress, not grades. Say "Needs practice", not "Weak" or "Failed".

**Instructor views**

- Assignment form: title, language, description, starter code, reference solution (clearly marked **Hidden from students**), constraints, maximum hint level.
- Class dashboard: sortable and filterable table of students, concept heat summary, drill-down per student, CSV export. Do not show student source code by default; show it only after an explicit "View attempt" action.

**Auth and onboarding**

- Short forms, inline validation, show or hide password, clear errors. Choose a path: **Practise on my own** or **Join a class**. First run shows a three-step, skippable tour of Run, Get hint and the ladder.

**Settings**

- Theme, editor font size, keyboard shortcuts, privacy statement (what the extension sends), delete my data.

### 9.5 States, feedback and microcopy

Design all states, not only the happy path:

| State | Rule |
|-------|------|
| Loading | Skeletons or a spinner with text ("Running your code"), never a blank panel |
| Empty | Invite an action ("No attempts yet. Run some code and ask for a hint.") |
| Error | Say what happened and how to fix it. No apology, no blame, no vague wording. Example: "The server did not respond. Your code is saved. Try again." |
| Success | Brief and specific, using the same verb as the action ("Fixed. Added to your history.") |
| Disabled | Always explain why |
| Timeout or sandbox kill | "Your program ran longer than 5 seconds and was stopped. Check for a loop that never ends." |

Writing rules: sentence case, active voice, plain verbs, one name per action across the whole product, no filler, no jargon, no blame ("Your code has an error on line 4", never "You made a mistake"). Buttons say exactly what happens ("Get hint", "Show solution", "Save assignment").

### 9.6 Accessibility (WCAG 2.2 AA is the floor)

- Full **keyboard operation** with a logical tab order, a visible 2 px focus ring on every interactive element, a skip-to-content link, and no keyboard traps (the Monaco editor must offer an escape route; document it).
- Semantic HTML and landmarks (`header`, `nav`, `main`). ARIA only where HTML is not enough.
- Every control has an accessible name. Dialogs trap focus, return focus on close, and close with Escape.
- Text resizes to 200 percent without loss. Layout reflows at 320 CSS px without horizontal scrolling (except the code editor).
- Colour is never the only signal. Contrast meets the numbers in 9.2 in both themes.
- Respect `prefers-reduced-motion` and `prefers-color-scheme`.
- Keyboard shortcuts (show in tooltips; avoid clashing with browser or VS Code defaults; make them configurable): Run `Ctrl/Cmd + Enter`, Get next hint `Ctrl/Cmd + Shift + H`, Toggle theme from the menu only.
- Test with a screen reader at least once per major screen (NVDA or VoiceOver) and with keyboard only.

### 9.7 Responsive behaviour

Breakpoints (guide): 360, 600, 900, 1280. Mobile gets read and light-use support (dashboard, hints, history); the editor works but is not the main target on phones. Use relative units, flexbox or grid, and no fixed pixel widths on containers.

### 9.8 Performance targets for a smooth feel

First contentful paint under 2 seconds on a normal connection; hint response shown within about 1 second after the backend replies; editor stays responsive during runs (run on the server, never block the UI thread); lazy-load the Monaco editor and the charts.

### 9.9 HCI evaluation (feeds the user study in weeks 14 to 15)

Instrument the app so we can measure: time to fix, hints used, level reached, task success, errors, and which interface was used (web or extension). Plan: a heuristic evaluation by two classmates using Nielsen's list, think-aloud sessions with 3 to 5 students, the **System Usability Scale (SUS)** questionnaire, and a short understanding quiz. Keep a `docs/hci-evaluation.md` for results.

---

## 10. Repository layout (proposal; confirm)

```
socracode/
  README.md  CLAUDE.md  DECISIONS.md  CHANGELOG.md
  docs/            architecture.md, api.md, hci-evaluation.md, datasets.md
  backend/
    app/ (api, runner, parser, rules, ml, retrieval, hints, student_model, db)
    tests/
    pyproject.toml
  web/
    src/ (components, features, theme, pages, lib)
    tests/
    package.json
  extension/
    src/  package.json
  ml/
    data/ (generated, heldout)  notebooks/  scripts/
  sandbox/         Dockerfile and runner config
  docker-compose.yml  .env.example
```

---

## 11. Working agreements and definition of done

For every step I give you:

1. **Plan first**, then code, then run instructions, then tests, then "what is next".
2. Keep changes **small and focused**. One concern per commit; suggest a clear commit message.
3. Python code is typed (type hints), formatted (Ruff) and tested (pytest). TypeScript is strict mode, linted and tested.
4. No dead code, no placeholder `TODO` left silently; list open items at the end of the message.
5. A step is **done** only when: it runs, tests pass, the UI works in **light and dark mode**, keyboard-only use works for new UI, and `DECISIONS.md` and docs are updated.
6. Explain anything non-obvious in plain language. I must be able to **explain every line in my viva**, so prefer clear code over clever code, and add short comments where the reasoning matters (especially the level gate, the sandbox, the classifier and the leak checks).
7. Ask me before: adding a dependency, changing the API contract, changing the data model, or changing any rule in section 2.

---

## 12. Your first reply

Reply with the five items from section 0 (summary, contradictions or gaps, questions, repository layout, and "waiting for Step 1"). Do not generate code in this reply.
