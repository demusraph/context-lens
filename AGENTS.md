# AGENTS.md: ContextLens Operational Protocol

## 1. Project Overview & Core Mission
**ContextLens** is a high-performance observability and semantic analysis engine designed to map complex codebases into vector-indexed knowledge graphs. The mission is to provide sub-millisecond retrieval of architectural dependencies and cross-file semantic relationships.

**Core Objective:** Maintain 100% type-safe, modular, and decoupled Python 3.11+ code. Agents must prioritize architectural integrity over feature velocity.

---

## 2. Local PowerShell Commands
All automation must be executed via the project root. Agents are required to verify environment state before execution.

*   **Environment Setup:** `.\scripts\setup.ps1` (Installs venv, syncs `pyproject.toml`, installs pre-commit hooks).
*   **Test Suite:** `pytest tests/ --cov=contextlens --cov-report=term-missing`
*   **Execution:** `python -m contextlens.main --config ./config/prod.yaml`
*   **Linting/Formatting:** `ruff check . --fix && ruff format .`
*   **Type Checking:** `mypy contextlens/ --strict --show-error-codes`

---

## 3. Engineering Invariants
Agents must strictly adhere to these constraints to maintain repository health:

1.  **Zero-Placeholder Mandate:** Never commit `TODO` blocks, `FIXME` comments, or "implement later" stubs without an associated GitHub Issue ID. All code must be production-ready upon submission.
2.  **Typing Strictness:** Every function, method, and class attribute must have explicit type hints. Use `typing.Protocol` for dependency injection and `Final` for constants. No `Any` types allowed without explicit architectural justification.
3.  **Line Endings:** Enforce `LF` (Line Feed) globally. Agents must configure their environment to ignore `CRLF` conversions.
4.  **Decoupling:** Business logic must be separated from I/O and infrastructure concerns. Use the Repository Pattern for data access; inject dependencies via constructor injection.
5.  **Error Handling:** No bare `except:` blocks. Catch specific exceptions and log via the standard `logging` module with structured metadata.

---

## 4. Self-Healing & Error Recovery Protocol
When a failure occurs, agents must follow this recursive recovery loop:

1.  **Traceback Analysis:** Extract the full stack trace. Identify the root cause (e.g., `AttributeError`, `ValidationError`, `ConnectionTimeout`).
2.  **State Inspection:** Run `pytest` on the failing module in isolation: `pytest tests/path/to/module.py`.
3.  **Hypothesis Generation:** Formulate a fix that adheres to the `ARCHITECTURE.md` design patterns.
4.  **Verification:**
    *   Apply the fix.
    *   Run `mypy` to ensure type safety.
    *   Run `ruff` to ensure style compliance.
    *   Execute the specific test case that failed.
5.  **Regression Check:** Run the full test suite to ensure no side effects in downstream modules.

---

## 5. Definition of Done (DoD) Quality Gate
A task is only "Done" when the following conditions are met:

*   **Functional:** All requirements in the PRD are implemented and verified via unit/integration tests.
*   **Test Coverage:** Minimum 90% branch coverage; critical paths must have 100% coverage.
*   **Static Analysis:** Zero errors reported by `mypy --strict` and `ruff`.
*   **Documentation:** All public APIs are documented with Google-style docstrings.
*   **Performance:** Execution time for core indexing functions remains within the defined latency budget (e.g., < 50ms for 1k nodes).
*   **Cleanliness:** No dead code, no unused imports, and no commented-out blocks.
*   **Peer Review:** The code has been reviewed against the `ARCHITECTURE.md` design patterns.