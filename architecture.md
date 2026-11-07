# Architecture: Hybrid RAG

## 1. System shape

Use a modular monolith for the MVP: a Next.js UI calls a FastAPI service; the API owns ingestion, retrieval, answer orchestration, evaluation hooks, and health endpoints. PostgreSQL is the source of truth for documents, chunks, lexical indexes, vectors, and evaluation metadata. Redis is an optional performance cache, never the source of truth. Compose runs the API, UI, PostgreSQL/pgvector, and Redis; Langfuse may be enabled as an optional local observability profile.

See [`design.mmd`](design.mmd) for the component flow.

## 2. Runtime components

- **Web UI:** Next.js App Router, TypeScript; no direct database access.
- **API:** FastAPI, typed request/response models, dependency-injected services.
- **Ingestion pipeline:** validate → hash → parse → normalize → chunk → embed → transactional upsert/activation.
- **Retrieval service:** parallel FTS and vector queries → RRF → top-20 reranker → selected context.
- **Answer service:** provider adapter, evidence-constrained prompt, citation validation, calibrated abstention.
- **PostgreSQL:** pgvector HNSW index and `tsvector` GIN index, migrations, connection pool.
- **Redis:** cache retrieval/answer results with corpus/model/prompt version in key; TTL and explicit invalidation/versioning.
- **Tracing:** OpenTelemetry-friendly internal trace model, exported through a Langfuse-compatible adapter when configured; local structured logs remain usable without Langfuse.

## 3. Data model

Use UUID primary keys, UTC timestamps, foreign keys, and migrations. Names are logical; exact SQL types can be adapted to the chosen ORM.

### `documents`

- `id UUID PRIMARY KEY`
- `source_uri TEXT NULL`, `source_name TEXT NOT NULL`, `mime_type TEXT NOT NULL`
- `metadata JSONB NOT NULL DEFAULT '{}'`
- `content_sha256 CHAR(64) NOT NULL`
- `version INTEGER NOT NULL`, `is_active BOOLEAN NOT NULL DEFAULT false`
- `parser_version TEXT NOT NULL`, `chunker_version TEXT NOT NULL`, `embedding_model TEXT NOT NULL`
- `status TEXT CHECK (status IN ('processing','active','failed','superseded'))`
- `created_at`, `updated_at`, `ingested_at TIMESTAMPTZ`
- Unique active identity constraint or transaction-enforced invariant on normalized `source_uri` (or source name when URI absent).

### `chunks`

- `id UUID PRIMARY KEY`, `document_id UUID REFERENCES documents(id) ON DELETE CASCADE`
- `ordinal INTEGER NOT NULL`, `text TEXT NOT NULL`, `token_count INTEGER NOT NULL`
- `location JSONB NOT NULL DEFAULT '{}'` (page, heading, URL fragment, offsets as available)
- `content_sha256 CHAR(64) NOT NULL`
- `embedding VECTOR(384) NOT NULL` for the default BGE-small model; dimension must be configurable/migration-safe if model changes.
- `search_vector TSVECTOR GENERATED OR MAINTAINED` using an English configuration by default.
- `created_at TIMESTAMPTZ NOT NULL`
- Unique `(document_id, ordinal)`; indexes for vector HNSW cosine ops, FTS GIN, active-document filtering, and document lookup.

### `ingestion_jobs` (recommended)

- `id UUID`, source/document reference, `status`, timestamps, stage/error summary, idempotency key.
- Store safe error codes/messages; do not store secrets or document body in errors.

### `feedback` (optional later phase)

- `id`, query/trace reference, selected chunk IDs, explicit rating, optional notes, timestamp, retention policy. Do not use for model training without a separately reviewed data policy.

## 4. API contract

All endpoints are versioned under `/api/v1`. Return consistent error bodies: `{ "error": { "code": "...", "message": "...", "request_id": "..." } }`.

- `GET /health/live` — process liveness.
- `GET /health/ready` — DB and required dependencies ready; optional providers reported separately.
- `POST /api/v1/documents` — multipart upload + optional metadata; returns `202` with document/job IDs and status. Support `Idempotency-Key`.
- `GET /api/v1/documents` — paginated document status/metadata.
- `GET /api/v1/documents/{document_id}` — details and active version.
- `DELETE /api/v1/documents/{document_id}` — remove/deactivate document and invalidate corpus cache version.
- `POST /api/v1/search` — `{query, top_k, mode: bm25|dense|hybrid, rerank, filters}`; returns ranked chunks, component ranks, scores, locations, trace ID, and stage timings.
- `POST /api/v1/answers` — `{query, top_k, filters}`; returns `{answer, citations[], abstained, trace_id, timings}`.
- `POST /api/v1/evaluations/run` — development/admin-only trigger or CLI equivalent; avoid exposing unrestricted in public deployments.

Do not expose raw embeddings or unrestricted SQL through the API. Validate all limits and filters.

## 5. Ingestion and idempotency

1. Enforce upload size/type and assign request ID; derive stable source identity from a supplied URI or normalized file name within the single-user local MVP.
2. Compute SHA-256 over raw bytes and normalized extracted text; record which hash drives deduplication. Default: raw bytes for exact upload idempotency plus normalized text hash for version/content diagnostics.
3. If same source identity and raw hash are already active with matching parser/chunker/embedder versions, return existing document/job as unchanged.
4. Extract with format-specific parser; preserve page/heading/URL locations. Reject empty/unreadable content with a useful failure.
5. Deterministically normalize and chunk. Generate embeddings in bounded batches with timeouts.
6. In a transaction, create the new version and chunks, then atomically activate it and mark prior version superseded. If any stage fails, leave previous active version untouched and mark the attempted job failed.
7. Increment a corpus-version counter and invalidate or version cache keys after successful activation or deletion.

If ingestion is synchronous initially, preserve job/status semantics so it can move to a worker later without changing the public contract.

## 6. Retrieval details

- **Lexical:** PostgreSQL `websearch_to_tsquery` (or explicitly documented parser) against `tsvector`; use rank ordering, deterministic tie-break by chunk ID. Call it BM25-style lexical search in product copy; PostgreSQL FTS ranking is not classic BM25 unless a BM25 extension is selected.
- **Dense:** query embedding, cosine distance against active chunks; HNSW cosine index. Set and report `hnsw.ef_search`; tune only with measured recall/latency.
- **Fusion:** RRF score `sum(1 / (k + rank_i))`, default `k=60`, for candidates found in one or both lists. Stable tie-breaks make output reproducible.
- **Rerank:** cross-encoder scores query/chunk pairs from the top 20 fused candidates; keep model calls bounded and stage-timed.
- **Answer:** include only top evidence within prompt/token budget. Require citation IDs to reference supplied chunks; validate and repair once or abstain. Never fabricate citation locations.
- **Filters:** apply document status and safe metadata filters consistently to both retrieval branches.

## 7. Cache policy

Cache retrieval and, optionally, answer results separately. Key includes normalized query, filters, mode, top-k, embedding/reranker/generator versions, prompt version, and corpus version. Default TTL 5 minutes for retrieval and 2 minutes for answers; configurable. Do not cache errors or empty results by default. Invalidate by corpus-version change; never rely on a manual key deletion as the only correctness mechanism. Record cache hit/miss and latency.

## 8. Security and privacy

- Localhost-only by default; document that exposing the service requires authentication, TLS, rate limits, and deployment review.
- Validate file type by content/magic where feasible, size, parser time, and extracted text size. Store uploads outside executable/static paths; use safe generated filenames.
- Parameterize SQL, validate metadata filters, protect against prompt injection by treating retrieved text as untrusted evidence, and prevent it from overriding system instructions or tool policy.
- Secrets only in environment/secret manager. `.env` is ignored; `.env.example` contains placeholders only.
- Minimize trace data. Redact tokens, credentials, and sensitive metadata; do not log full document text or full prompts by default.
- Set explicit timeouts and bounded retries for model/database calls. Avoid retrying non-idempotent operations without an idempotency key.

## 9. Observability and failure handling

Every request has a request/trace ID. Emit stage names and duration for parse, embed, lexical, dense, fusion, rerank, generation, and serialization; candidate counts; model/version; cache result; safe error code. Expose dependency health without returning secrets. Distinguish unavailable optional integrations from required database failure. Use structured logs and a Langfuse adapter that degrades cleanly when disabled.

## 10. Deployment and migrations

Compose services use pinned compatible major versions, persistent named DB volume, health checks, non-root app containers where practical, and explicit resource/config settings. Database schema changes use migrations; startup must not silently mutate production schema. Provide a clean local reset command with a clear data-loss warning. Never put user documents or credentials in the image.

## 11. Architecture decision records

Record meaningful changes: vector store, embedding model/dimension, parser, chunking, answer provider, cache policy, deployment/authentication. For each record include context, decision, alternatives, impact, and migration/re-embedding implications.

