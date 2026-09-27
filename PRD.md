# Product Requirement Document (PRD)

## Project: ContextLens (`context-lens`)
**Tagline:** Semantic & AST Context Pruner for LLM Coding Agents (60–80% Token Reduction)  
**Category:** Agentic AI Systems / Context Engineering Infrastructure  

---

## 1. Executive Summary & Problem-Solution Fit

### 1.1 Executive Summary
`context-lens` is a high-performance Python SDK, CLI, and real-time visualization tool designed to resolve context window bloat in LLM-driven coding agents (e.g., AutoGen, CrewAI, LangGraph, OpenDevin, Cursor-like custom engines). By transforming raw source code files into Syntactic Symbol Graphs (SSG) and stripping implementation logic while retaining explicit interfaces, typing, docstrings, and import hierarchies, ContextLens reduces token consumption by **60% to 80%** without loss of structural or semantic reasoning capacity.

### 1.2 Problem Statement
Modern agentic software engineering pipelines ingest entire code repos or multi-file context trees into LLM prompt buffers. As repositories grow, passing full implementation details (loop bodies, internal variable allocations, private helper functions) leads to:
1. **Extreme Token Costs:** Multi-turn agent conversations re-send thousands of lines of boilerplate code on every turn, inflating API bills exponentially.
2. **Context Window Rot & Attention Degradation:** Large prompt payloads cause performance degradation ("lost-in-the-middle" phenomena), increasing hallucination rates in LLMs when modifying cross-file interfaces.
3. **Latency Bottlenecks:** High input token counts increase Time-To-First-Token (TTFT) and overall agent turn latency across inference providers.
4. **Context Window Truncation:** Critical import definitions or type signatures are evicted from the context window during long-running tasks.

### 1.3 Solution Architecture
ContextLens sits between the codebase retriever and the LLM prompt composer. It employs deterministic Abstract Syntax Tree (AST) parsing via native libraries and Tree-sitter bindings to extract structural skeletons.

```
+-------------------+      +-----------------------+      +--------------------------+      +-------------------+
|  Raw Source Files | ---> | ContextLens Engine    | ---> | Lightweight Skeleton     | ---> | LLM Context Window|
| (Py, TS, Go)      |      | (AST + Import Mapper) |      | (Signatures + Types)     |      | (20-40% Token Size|
+-------------------+      +-----------------------+      +--------------------------+      +-------------------+
                                       |
                                       v
                           +-----------------------+
                           | In-Browser Cockpit    |
                           | (Token Delta Viewer)  |
                           +-----------------------+
```

---

## 2. Target Personas & Core User Stories

### 2.1 Target Personas

| Persona ID | Role | Key Objectives | Pain Points |
| :--- | :--- | :--- | :--- |
| **P-01** | **Agentic AI Infrastructure Engineer** | Build resilient, low-latency LLM coding workflows with strict context budgets. | Reaching context limits (32k/128k/200k tokens) during multi-file refactoring tasks. |
| **P-02** | **DevOps / AI Platform Lead** | Reduce Enterprise OpenAI/Anthropic monthly API spend on internal coding assistants. | Unbounded token cost scaling across developer engineering teams. |
| **P-03** | **Developer Tooling Architect** | Integrate intelligent context reduction into IDE extensions, local CLI tools, or CI/CD feedback loops. | Naive line-based or character-based truncation breaking code syntax and language server context. |

### 2.2 Core User Stories

#### US-01: Python, TypeScript, and Go AST Skeletonization
* **As an** Agentic AI Infrastructure Engineer,
* **I want to** pass Python (`.py`), TypeScript (`.ts`, `.tsx`), and Go (`.go`) source files through ContextLens,
* **So that** function and method bodies are replaced with pass-through indicators (`...` or `panic("not implemented")`) while preserving function signatures, class interfaces, type annotations, decorators, and public docstrings.
* **Acceptance Criteria:**
  - Python files parsed via native `ast` module; TS and Go parsed via unified `tree-sitter` native bindings.
  - Generates syntactically valid code skeletons for all three target languages.
  - Retains 100% of class definitions, interface definitions, method/function parameters, return types, and docstrings.
  - Drops function/method execution bodies, internal private closures, and localized statement blocks.

#### US-02: Import Reference Resolution & Tree Pruning
* **As an** Agentic AI Infrastructure Engineer,
* **I want** ContextLens to map cross-file import dependencies within a target project directory,
* **So that** referenced external types and symbols are retained at full detail while unreferenced utility functions are aggressively pruned.
* **Acceptance Criteria:**
  - Builds an in-memory Dependency Import Graph (DIG) mapping relative and absolute imports across the codebase.
  - Dynamically adjusts pruning depth based on target symbol queries (e.g., if `UserService` is target, keep `User` model interface full; skeletonize unreferenced `AuthHelper`).

#### US-03: Real-Time Token Footprint Reduction Calculator
* **As a** DevOps / AI Platform Lead,
* **I want** the engine to output precise token counts and percentage reduction metrics (raw vs. pruned),
* **So that** I can dynamically audit token savings and programmatically adjust pruning aggressiveness.
* **Acceptance Criteria:**
  - Computes exact token count using `tiktoken` (`cl100k_base`, `o200k_base`) or HuggingFace tokenizers.
  - Returns a structured payload containing `raw_tokens`, `pruned_tokens`, `reduction_percentage`, and `processing_time_ms`.

#### US-04: Interactive In-Browser Comparison Cockpit
* **As a** Developer Tooling Architect,
* **I want** an interactive local Web visualizer,
* **So that** I can inspect raw vs. pruned code side-by-side, analyze token diff heatmaps, and fine-tune retention thresholds before deploying rules to production agents.
* **Acceptance Criteria:**
  - FastAPI-backed local web interface launching via `context-lens UI --port 8080`.
  - Side-by-side Monaco editor displaying original code and pruned code with syntax highlighting.
  - Real-time token counter, compression percentage gauge, and AST node selection tree.

#### US-05: Programmatic Python SDK Integration
* **As an** Agentic AI Infrastructure Engineer,
* **I want to** import `context-lens` as a Python package (`pip install context-lens`),
* **So that** I can embed pruning directly into my LangGraph/CrewAI context pipeline via an async middleware function.
* **Acceptance Criteria:**
  - Zero required runtime network calls.
  - Async-native interface: `pruned_code = await pruner.aprune_file(path, strategy="balanced")`.
  - Type-hinted API compliant with `mypy --strict`.

---

## 3. MoSCoW Feature Matrix

```
+---------------------------------------------------------------------------------------------------+
|                                      MoSCoW FEATURE MATRIX                                        |
+------------------------------------+------------------------------------+-------------------------+
| MUST-HAVE (P0)                     | SHOULD-HAVE (P1)                   | DELIGHT / NICE-TO-HAVE  |
| Core Engine & AST Parsers          | Advanced Routing & UI              | (P2) Extensions         |
+------------------------------------+------------------------------------+-------------------------+
| - Python Native AST Pruner         | - Interactive Web Cockpit UI       | - Rust, C++, Java Parsers|
| - TypeScript Tree-Sitter Pruner    | - Configurable Retention Profiles  | - LLM Attention Density |
| - Go Tree-Sitter Pruner            | - Import Path Resolution Graph     |   Feedback Integration  |
| - Tiktoken Token Delta Engine      | - Disk & In-Memory AST LRU Cache  | - Git Diff-Aware        |
| - Python SDK (`context_lens`)      | - CLI Tool (`context-lens run`)    |   Selective Pruning     |
| - Async Middleware Interfaces      | - Token Saving Heatmap Generator   | - IDE Plugin Interop    |
+------------------------------------+------------------------------------+-------------------------+
```

### 3.1 P0 - Must-Have (Release Target v1.0.0)
* **P0-1: Multi-Language Skeletonizer Engine**
  * Execution of syntactic stripping for Python 3.11+, TypeScript 5.0+, and Go 1.21+.
  * Complete preservation of function signatures, arguments, type annotations, return types, class structures, public interfaces, and docstrings.
  * Body replacement with language-appropriate valid syntax (`pass` or `...` for Python, `{}` for TS, `panic("stub")` or empty block for Go).
* **P0-2: Token Delta Calculator Engine**
  * Integration with `tiktoken` for OpenAI token models (`cl100k_base`, `o200k_base`) and configurable fallback to HuggingFace `AutoTokenizer` for open models (e.g., Llama-3, Qwen-2.5).
  * Direct structural computation of input/output token deltas.
* **P0-3: Dependency Import Resolver**
  * Analysis of local file system imports (e.g., `from .models import User`) to construct an internal dependency map and avoid stripping referenced cross-file dynamic types.
* **P0-4: Fully Typed Async Python SDK**
  * Thread-safe, non-blocking Python SDK exposed via async/await execution contracts.

### 3.2 P1 - Should-Have (Release Target v1.1.0)
* **P1-1: In-Browser Comparison Cockpit**
  * Local web UI embedded via FastAPI and static Single Page Application (React/Tailwind).
  * Interactive AST node toggle tree allowing engineers to visually disable/enable docstrings, private functions, or type annotations to inspect token impact in real time.
* **P1-2: Context Retention Profiles**
  * Pre-configured pruning strategies:
    * `AGGRESSIVE`: Strips all docstrings, keeps signatures and types only (~75-85% reduction).
    * `BALANCED` (Default): Keeps public docstrings, signatures, type definitions, and exports (~60-70% reduction).
    * `INTERFACE_ONLY`: Strips all private methods/functions (`_method`), keeps exported/public interfaces (~70-80% reduction).
* **P1-3: AST In-Memory & Disk Cache**
  * SHA-256 content hashing of source files to cache AST representations, avoiding re-parsing unchanged repository files.
* **P1-4: CLI Production Tooling**
  * Command-line binary interface supporting folder-level skeletonization, direct file piping, and JSON summary outputs.

### 3.3 P2 - Delight / Nice-To-Have (Release Target v1.2.0+)
* **P2-1: Extended Tree-Sitter Language Support**
  * AST skeletonization modules for Rust (`.rs`), C++ (`.cpp`, `.hpp`), and Java (`.java`).
* **P2-2: Git Diff-Aware Selective Pruning**
  * Capability to parse `git status` / `git diff`: files modified in the active branch remain full-body, while unmodified dependency context files are automatically skeletonized.
* **P2-3: LLM Context Attention Feedback Integration**
  * Dynamic context expansion: automatically restores stripped function bodies if an LLM returns a structured tool call requesting full body inspection for a specific symbol.

---

## 4. Non-Functional Requirements (NFRs)

### 4.1 Performance & Latency
* **Parsing Latency (p95):** $\le 15\text{ ms}$ per 1,000 Lines of Code (LOC) on a single CPU core.
* **Multi-File Batch Latency (p95):** Processing a 100-file repository (~50,000 LOC) must execute in $\le 450\text{ ms}$ using multi-threaded worker pools.
* **Memory Footprint:** Baseline RSS overhead $\le 80\text{ MB}$. Peak memory allocation during multi-file AST graph generation must not exceed $250\text{ MB}$.

```
LATENCY TARGETS (p95)
+------------------------------------+-----------------------+
| Operation                          | Maximum Allowed Time  |
+------------------------------------+-----------------------+
| Single File Skeletonization (1k LOC)| 15 ms                 |
| Single File Skeletonization (10k)  | 50 ms                 |
| Token Delta Calculation (Tiktoken) | 5 ms                  |
| Import Graph Build (100 files)     | 200 ms                |
| Total SDK Overhead per LLM Turn    | < 25 ms               |
+------------------------------------+-----------------------+
```

### 4.2 Security, Privacy & Air-Gapped Operation
* **100% Offline Capability:** Zero outbound network traffic. AST parsing, token estimation, and import graph resolution execute completely locally.
* **No Code Ingestion / Storage:** ContextLens operates strictly in-memory during SDK execution; source code is never cached to third-party services or remote logs.
* **Dependency Safety:** Minimal runtime dependencies. Tree-sitter parsers sandboxed via native bindings without sub-process execution calls.

### 4.3 Reliability & Determinism
* **Deterministic Execution:** Given an identical source file and pruning profile, ContextLens must produce bit-for-bit identical skeleton outputs and token counts every time.
* **Syntax Validity Guarantee:** Pruned output code must maintain 100% valid syntax. The output must pass native compiler/parser validation (e.g., `python -m py_compile`, `tsc --noEmit`, `go vet`).

### 4.4 Portability & System Compatibility
* **Python Compatibility:** Python 3.11, 3.12, 3.13.
* **Operating Systems:** Linux (x86_64, aarch64), macOS (Intel, Apple Silicon), Windows (x64).
* **SDK Standards:** Fully typed with strict static analysis (`mypy --strict`, `ruff` compliance).

---

## 5. Quantitative Success Metrics & KPIs

### 5.1 Primary Performance KPIs

$$\text{Token Reduction Rate (\%)} = \left( 1 - \frac{\text{Tokens}_{\text{Pruned}}}{\text{Tokens}_{\text{Raw}}} \right) \times 100$$

* **Target Target Mean Reduction:** $\ge 65\%$ across mixed-language benchmark repos (e.g., Django, VS Code extension core, Kubernetes utilities).
* **Target Aggressive Profile Reduction:** $\ge 78\%$.

### 5.2 Reasoning Quality & Context Accuracy KPIs
* **Agent Task Completion Success Rate (SWE-bench Subset):** LLM coding agents supplied with ContextLens-pruned contexts must maintain $\ge 96\%$ of the task completion success rate achieved when supplied with full raw source files.
* **Zero Syntax Failure Rate:** $0\%$ syntax error exceptions thrown by down-stream agent linters or compilers due to invalid pruned output syntax.

### 5.3 System Efficiency KPIs

```
Metric                             Target Threshold
------------------------------------------------------------
Processing Throughput              >= 50,000 LOC / second
Inference Cost Savings             60% - 80% reduction in input token API cost
Time-To-First-Token (TTFT) Improvement 25% - 40% reduction due to smaller prompt payloads
SDK Overhead Ratio                 < 2% of total agent turn duration
```

---

## 6. Detailed System Component Specifications

### 6.1 AST Pruning Engine Rules

#### Python Pruning Rules
1. **Modules / Files:** Preserve file-level docstrings, top-level type aliases, global constants, and module imports (`import`, `from ... import ...`).
2. **Classes:** Preserve class decorators, base class inheritances, class-level type annotations, and inner docstrings.
3. **Methods & Functions:** Preserve function decorators, `async` keywords, full argument signature lists, parameter type hints, return type annotations, and docstrings.
4. **Body Execution Statements:** Replace statement block with `...` (Ellipsis).

#### TypeScript Pruning Rules
1. **Modules / Imports:** Preserve `import` declarations, `export` statements, namespaces, and top-level type/interface definitions.
2. **Classes & Interfaces:** Preserve `interface`, `type`, `enum`, class method signatures, access modifiers (`public`, `private`, `protected`), and property types.
3. **Functions & Methods:** Preserve generics specifications (`<T>`), argument types, return types, and JSDoc comment blocks (`/** ... */`).
4. **Body Execution Statements:** Replace function body blocks `{ ... }` with `{}` or empty implementation body.

#### Go Pruning Rules
1. **Packages / Imports:** Preserve `package` declaration, `import (...)` blocks.
2. **Structs & Interfaces:** Preserve struct field tags, type aliases, interface method signatures.
3. **Functions & Methods:** Preserve receiver parameters `(s *Service)`, argument name-type pairs, and return type declarations.
4. **Body Execution Statements:** Replace function body `{ ... }` with `panic("stub")`.

---

## 7. Comparison Cockpit UI Architecture

The comparison cockpit provides visual proof of pruning efficiency.

```
+-----------------------------------------------------------------------------------------+
| ContextLens Cockpit v1.0                                       [ Profile: BALANCED v ]   |
+-----------------------------------------------------------------------------------------+
| Files: src/services/user.ts                                                             |
+---------------------------------------------------+-------------------------------------+
| Raw Code (1,420 Tokens)                           | Pruned Code (310 Tokens)            |
| 60-80% Token Reduction Active                     | Reduction: 78.1%                    |
+---------------------------------------------------+-------------------------------------+
| 01 | import { DbClient } from '../db';            | 01 | import { DbClient } from '../db';|
| 02 |                                              | 02 |                                |
| 03 | /** Manages user lifecycle operations */     | 03 | /** Manages user lifecycle */  |
| 04 | export class UserService {                   | 04 | export class UserService {      |
| 05 |   private db: DbClient;                      | 05 |   private db: DbClient;         |
| 06 |                                              | 06 |                                |
| 07 |   async getUser(id: string): Promise<User> { | 07 |   async getUser(id: string):    |
| 08 |     const res = await this.db.query(...);    |    |     Promise<User> {};           |
| 09 |     if (!res) throw new Error("NotFound");   | 08 |                                |
| 10 |     return new User(res.row);                | 09 |   async deleteUser(id: string): |
| 11 |   }                                          |    |     Promise<void> {};           |
| 12 | }                                            | 10 | }                              |
+---------------------------------------------------+-------------------------------------+
| Token Metrics: Original: 1,420 | Skeleton: 310 | Delta: -1,110 Tokens (-78.1%)          |
+-----------------------------------------------------------------------------------------+
```

### 7.1 Cockpit Functional Requirements
1. **Dual Monaco Editors:** Synchronized scrolling between original source code view and skeletonized pruned view.
2. **Visual Token Heatmap:** Highlighting removed AST nodes in subtle red background hues on the raw editor panel.
3. **Interactive Control Bar:**
   * Profile Selector dropdown (`AGGRESSIVE`, `BALANCED`, `INTERFACE_ONLY`).
   * Node Toggles: Checkboxes for `Keep Docstrings`, `Keep Private Methods`, `Keep Internal Imports`.
   * Model Tokenizer Selector: Switch between `cl100k_base` (GPT-4o), `o200k_base` (GPT-4o-mini), and custom HuggingFace tokenizers.
4. **Metric Telemetry Panel:** Live calculated values for Raw Tokens, Skeleton Tokens, Net Delta, Compression Ratio, and AST Extraction Processing Time (ms).