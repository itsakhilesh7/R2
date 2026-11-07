# Hybrid RAG Starter Pack

This folder is the project brief and build guide for a production-style hybrid retrieval-augmented generation (RAG) MVP. Copy it into the root of a new or existing Codex project, then paste [`CODEX_PROMPT.md`](CODEX_PROMPT.md) as the first task.

## Defaults

- API: Python 3.12, FastAPI, Pydantic
- Storage and retrieval: PostgreSQL 16 with pgvector; PostgreSQL full-text search for lexical retrieval
- Embeddings: configurable provider behind an interface; local Sentence Transformers default using `BAAI/bge-small-en-v1.5` (384 dimensions) for a lightweight starter. Keep model and dimensions configurable.
- Reranking: `BAAI/bge-reranker-base` on at most the top 20 fused candidates
- Fusion: reciprocal rank fusion (RRF)
- Cache: Redis, with versioned keys and invalidation on corpus changes
- UI: Next.js App Router, TypeScript
- Operations: Docker Compose; Langfuse-compatible trace interface with a no-op/local implementation

The initial embedding default is intentionally smaller than the reranker to reduce local setup cost; document any change and re-embed on model changes. Do not claim benchmark results until measured on the included evaluation set.

## Files

- `prd.md` — user needs, scope, acceptance criteria
- `architecture.md` — components, data model, APIs, retrieval and ingestion design
- `rules.md` — engineering and security constraints
- `agent-workflow.md` — phase gates and Codex collaboration rules (the distinct second rules-related file)
- `phases.md` — 35–45 hour staged plan
- `design.mmd` — Mermaid system diagram; this replaces the ambiguous `design.ms` request
- `CODEX_PROMPT.md` — staged first prompt for Codex
- `eval-plan.md` — evaluation methods, targets, and regression gates
- `eval-schema.json` — JSON Schema for the 80+ question evaluation set
- `.env.example` — local configuration template with no secrets

## Start

1. Put this folder's contents at the project root (or give Codex this folder as project context).
2. Open `CODEX_PROMPT.md` and submit its prompt.
3. Keep the implementation phase-gated. The initial Codex response should inspect the repository, identify assumptions, and propose Phase 0 only; it should not generate the whole application.
4. Build the evaluation set from documents you are allowed to use. Keep expected evidence spans and document metadata stable so metrics are reproducible.

## Scope boundary

The MVP supports PDF, HTML, and Markdown ingestion, metadata and content-hash idempotency, hybrid search, reranking, cited answers, an evaluation set of at least 80 questions, observability, Docker Compose, and a usable Next.js UI. Query routing, semantic caching, feedback-driven hard negatives, authentication providers, multi-tenancy, and distributed ingestion are later work unless a phase review explicitly promotes one.

All latency and retrieval numbers in the pack are targets or gates to validate locally, not achieved claims. Hardware, model provider, corpus, and dataset affect results.

## Phase 0 decisions

See [ADR 0001](docs/adr/0001-phase-0-project-decisions.md) for the decision record and unresolved inputs.

- **Ingestion identity:** unchanged content is identified by stable source identity, raw-byte SHA-256, and matching parser/chunker/embedder pipeline versions. Also store a normalized-text SHA-256 for content diagnostics and reproducibility.
- **Lexical retrieval terminology:** call PostgreSQL full-text search “FTS” or “BM25-style lexical retrieval.” Do not label it BM25 unless actual BM25 scoring is implemented.
- **Embedding changes:** changing embedding dimensions requires a database migration and a full re-embed. Record model/dimension changes and their migration impact in an ADR.
- **Chunking default:** use a configurable 350–400 token range, with 400 tokens as the initial default and 100-token overlap retained. Count with the embedding model tokenizer. Chunk size is an evaluation ablation axis.
- **Model input limits:** the BAAI model cards report a 512-token sequence length for `BAAI/bge-small-en-v1.5` and `BAAI/bge-reranker-base`. Enforce tokenizer-based limits and verify reranker query-plus-passage pairs fit the reranker limit.
- **Evaluation labels:** store source identity and an evidence quote/span, not corpus-specific chunk IDs. Resolve evidence to chunk IDs against the ingested corpus at evaluation runtime.
- **Phase ownership:** Codex will scaffold Docker, UI, and boilerplate. The user will hand-write chunking, ingestion activation, RRF, and evaluation metrics. Codex will review that code. At each phase gate, Codex will ask the user to explain 2–3 design decisions before proceeding.
- **Pending inputs:** sample corpus and Phase 4 answer-generation choice (Ollama model or free API) remain TBD. Reference machine: Intel Core i7-10510U (1.80/2.30 GHz), 8 GB RAM (7.57 GB usable), Intel UHD Graphics (128 MB). Do not invent benchmark claims before a reproducible run.

## Phase 1: local skeleton

This phase adds a FastAPI service, a Next.js App Router landing page, PostgreSQL 16 with pgvector, Redis, validated environment settings, and an Alembic migration that only enables the `vector` extension. Documents/chunks tables and model loading are intentionally deferred.

### Requirements

- Docker Desktop with Compose v2
- Python 3.12 and [uv](https://docs.astral.sh/uv/)
- Node.js 22 and npm

### Run the stack

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose exec api uv run --project /app alembic upgrade head
```

Open the UI at <http://localhost:3000>. The API liveness endpoint is <http://localhost:8000/health/live>; readiness is <http://localhost:8000/health/ready> and returns HTTP 503 until PostgreSQL responds. To view service status and logs, run `docker compose ps` and `docker compose logs -f api web db redis`.

For local Python development outside Compose, run `uv sync --project apps/api`, set `DATABASE_URL` to a local PostgreSQL URL and `REDIS_URL` to a local Redis URL, then run `uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head` and `uv run --project apps/api uvicorn hybrid_rag_api.main:app --reload --app-dir apps/api/src`.

For local UI development outside Compose, run `npm ci` and `npm run dev` from `apps/web`.

### Local resource limits

Compose caps PostgreSQL at 1.5 GiB/1.5 CPU, Redis at 384 MiB/0.5 CPU, the API at 1.5 GiB/1.5 CPU, and the UI at 1 GiB/1 CPU (4.375 GiB and 4.5 CPUs total). These limits leave memory and CPU headroom on the documented 8 GB Intel laptop. No embedding or reranker model is downloaded or loaded in Phase 1.

To stop the services, run `docker compose down`. To also remove the persisted database and Redis data, run `docker compose down --volumes` (destructive).

