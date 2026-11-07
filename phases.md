# Delivery Phases (35–45 hours total)

Estimates are active implementation time for an intermediate developer, excluding lengthy model downloads and user review. Keep the MVP to roughly 35–45 hours. At each gate, report actual time and scope changes.

## Phase 0 — Repository reconnaissance and decisions (2–3 h)

Inspect repo and instructions; agree on runtime, package manager, embedding/answer provider defaults, local resource constraints, and sample corpus approach. Record decisions and a short execution plan.

**Acceptance:** repository map and conflicts documented; architecture decisions recorded; no speculative application-wide rewrite.

## Phase 1 — Skeleton and local infrastructure (4–5 h)

Create API/UI scaffolds, Compose services for PostgreSQL+pgvector and Redis, health checks, configuration validation, migrations framework, and basic documentation.

**Acceptance:** clean local start; readiness verifies database; migrations run; secrets absent from repository; UI and API respond.

## Phase 2 — Ingestion and provenance (6–7 h)

Implement PDF/HTML/Markdown validation and extraction, normalization, deterministic chunking, metadata/location preservation, hashing, versioning, and transactional activation.

**Acceptance:** fixture-based parser tests; unchanged source is idempotent; changed source produces a new active version; failed re-ingestion leaves old version available; document list/status API works.

## Phase 3 — Search, hybrid fusion, and reranking (7–8 h)

Implement embedding adapter, pgvector HNSW dense retrieval, PostgreSQL FTS lexical retrieval, RRF, top-20 reranking, filters, and retrieval-only API.

**Acceptance:** exact identifiers and semantic queries return expected evidence; component ranks and timings observable; deterministic RRF tests; reranker degradation is explicit; search works with cache disabled.

## Phase 4 — Grounded answers and citations (4–5 h)

Add answer-provider interface, evidence-limited prompt, citations, validation, abstention behavior, answer endpoint, and UI query flow.

**Acceptance:** citations point to returned/stored chunks and locations; no-evidence cases abstain; malformed citations are rejected/repaired; provider failures return safe errors.

## Phase 5 — Evaluation, traces, and cache (6–7 h)

Build dataset harness (minimum 80 questions), retrieval/answer metrics, ablations, latency percentiles, versioned Redis keys, traces, and baseline comparison.

**Acceptance:** report includes BM25/FTS, dense, hybrid, and reranked hybrid; metrics are reproducible; trace includes stage timings and cache outcome; dataset schema validated; baseline metadata recorded.

## Phase 6 — CI gates, hardening, and handoff (5–7 h)

Add automated checks, DB integration coverage, evaluation regression gate, Compose smoke path, error handling/security review, and final runbook.

**Acceptance:** CI runs deterministic tests; recall regression gate is enabled only with a reviewed baseline and dataset; fresh setup is documented; measured results clearly distinguish targets from observations; known limitations and next steps listed.

## Scope control

If implementation exceeds 45 hours, preserve ingestion correctness, hybrid retrieval, citations, and reproducible evaluation first. Reduce UI polish before cutting core retrieval/evaluation. Put query routing, semantic caching, feedback-driven hard negatives, auth integrations, and scaling beyond a single local Compose stack in follow-up work.

