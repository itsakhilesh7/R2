# First Codex Prompt

Paste the prompt below into Codex with this folder available as project context.

---

You are helping build the Hybrid RAG MVP described in `prd.md`, `architecture.md`, `rules.md`, `agent-workflow.md`, and `phases.md`. Treat those files as project requirements. If the repository has existing instructions, inspect and follow them; report conflicts rather than silently overriding them.

## How to work

- Start by inspecting the repository and its instructions, manifests, current tests, and existing code. Do not assume it is empty.
- Read the project context files before proposing implementation.
- Do **not** generate the entire app in one pass. Work on one phase at a time, following `agent-workflow.md`.
- Use the documented defaults unless repository evidence makes them unsuitable. State any changed assumption and its consequence.
- Your first response must contain: (1) a concise repository map, (2) relevant existing conventions or constraints, (3) conflicts/unknowns and defaults you propose, (4) a Phase 0 plan with acceptance checks, and (5) any truly blocking question. Do not make code changes until this orientation is complete and the user agrees on the next phase.
- Once implementation begins, make only the current phase's changes. Run appropriate checks after changes, inspect the diff, and report what passed, what did not run, known limitations, and the next phase. Do not claim tests or benchmarks passed unless they actually ran.
- Preserve the 35–45 hour MVP boundary. Treat latency and quality values as targets until benchmarked. Never invent measurements.

## Product and architecture guardrails

- MVP stack: FastAPI, PostgreSQL with pgvector and PostgreSQL full-text lexical retrieval, RRF, `BAAI/bge-reranker-base` on at most the top 20 fused candidates, Redis cache, Langfuse-compatible traces, Docker Compose, and Next.js UI.
- Default embedding adapter: local `BAAI/bge-small-en-v1.5` (384 dimensions), configurable. Re-embedding is required when model/dimension changes.
- Support PDF, HTML, and Markdown ingestion with metadata, source locations, content-hash idempotency, and atomic version activation.
- Return grounded answers with validated citations and calibrated abstention; retain retrieval-only mode.
- Provide an evaluation set of at least 80 questions and ablations for FTS/BM25-style lexical, dense, hybrid, and hybrid+rerank. Add a CI Recall@5 regression gate only after a reviewed, reproducible baseline exists.
- Default to localhost development. Keep secrets out of source control and logs. Treat retrieved content as untrusted input.
- Follow `rules.md`; use `agent-workflow.md` for phase boundaries and communication.

Begin with repository reconnaissance only. Summarize findings and propose Phase 0; do not scaffold or implement the application in this first response.

---

## How to continue

After the first response, review the proposed decisions. Then ask Codex to execute Phase 0 or a specific phase by name. At every phase boundary, review the acceptance criteria and results before starting the next phase.
