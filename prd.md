# Product Requirements: Hybrid RAG MVP

## 1. Product summary

Build a locally runnable, production-minded reference application that ingests a small knowledge corpus and answers questions using lexical and dense retrieval, RRF fusion, cross-encoder reranking, and source citations. The system should make retrieval quality, freshness, and latency measurable rather than hiding them behind a chat interface.

## 2. Problem

Dense retrieval can miss exact identifiers such as section numbers, tickers, filenames, and error codes. A useful RAG service must combine lexical matching with semantic similarity, rerank candidates, track document freshness, return evidence, and expose enough telemetry to diagnose failures.

## 3. Users and primary jobs

- **Developer/operator:** configure the service, ingest sources, inspect ingestion outcomes, and reproduce retrieval/evaluation runs.
- **Knowledge worker:** ask a question, see a grounded answer with citations, inspect cited passages, and recognize when the corpus does not support an answer.

## 4. MVP user journeys

1. Start the stack locally with Docker Compose and follow the README setup instructions.
2. Submit a PDF, HTML, or Markdown source with optional metadata; receive a stable document ID and ingestion status.
3. Re-submit unchanged content without creating duplicate chunks; changed content creates a new document version and retires old chunks atomically.
4. Ask a question; receive an answer, citations that map to source and chunk locations, and an abstention when evidence is insufficient.
5. Inspect retrieval mode, candidate ranks/scores, latency stages, cache status, and trace ID without exposing secrets or full sensitive content in logs.
6. Run the evaluation suite and compare BM25, dense, hybrid, and hybrid-plus-rerank results.

## 5. Functional requirements

### Ingestion

- Accept PDF, HTML, and Markdown through a documented API and UI upload flow.
- Validate type and size; default maximum upload is 25 MiB, configurable.
- Extract text with page/heading/URL provenance where available; report extraction warnings and failures clearly.
- Normalize text deterministically, split into configurable chunks (default 700 tokens, 100-token overlap), and retain source locations.
- Store source metadata, content hash, parser/chunker/embedding versions, timestamps, and status.
- Use a SHA-256 hash of normalized source bytes plus a stable source identity for idempotency. Repeated unchanged ingestion is a no-op; changed content is versioned and replaces active chunks transactionally.
- Never mark a source active until extraction, chunking, embedding, and persistence complete. Failed ingestion must not leave a partially active version.

### Retrieval and answer

- Perform PostgreSQL FTS lexical retrieval and pgvector cosine-distance dense retrieval independently.
- Fuse ranked lists with configurable RRF (default constant `k=60`), deduplicate by chunk ID, and pass at most 20 candidates to the cross-encoder.
- Rerank with `BAAI/bge-reranker-base`, configurable behind an interface. If unavailable, fail clearly or use an explicitly configured degraded mode; do not silently claim reranking occurred.
- Return a grounded answer with citations referencing document ID, title, chunk ID, and page/heading/URL location when available.
- Abstain when retrieved evidence is below a configurable relevance threshold or answer generation has no adequate evidence. The threshold must be calibrated on evaluation data.
- Provide retrieval-only mode for debugging and evaluation.
- Keep answer generation behind a provider interface, with a documented configurable default. No API key is required for retrieval-only mode. Do not hard-code provider credentials.

### UI

- Show document list/status and support upload, deletion, and re-ingestion.
- Provide a chat/search view with citations that open their source context.
- Show a compact “sources and retrieval” panel with trace ID and stage timings; make detailed scores an expandable diagnostic.
- Explain empty corpus, ingestion failure, and service unavailable states.

### Evaluation and operations

- Include a versioned JSONL or JSON evaluation dataset with at least 80 questions before the release gate is enabled; include exact-term and semantic cases, expected relevant chunk IDs or evidence spans, and answerability.
- Measure Recall@5 and Recall@10, MRR@10, nDCG@10, citation/evidence validity, answer correctness/faithfulness via a documented method, and p50/p95 end-to-end and stage latency.
- Produce an ablation report for BM25, dense, hybrid, and hybrid + rerank.
- Emit structured traces with request/trace ID, stage duration, candidate counts, cache outcome, model/version, and errors. Redact secrets and avoid logging full prompts or source text by default.
- Include health/readiness endpoints and container health checks.

## 6. Nonfunctional requirements and targets

These are initial targets to measure on a declared local reference machine and small benchmark corpus, not promises:

- Retrieval endpoint p50 ≤ 500 ms and p95 ≤ 1,500 ms, excluding external answer-generation provider latency, for a warm local corpus of up to 10,000 chunks.
- Full answer p50 ≤ 4 s and p95 ≤ 10 s when using a configured local or remote generation provider; report provider and hardware.
- Retrieval quality: hybrid+rerank Recall@5 should be at least 5 percentage points higher than the better of BM25-only/dense-only on the fixed evaluation set, without a material regression in nDCG@10. Treat this as a project goal, not a guaranteed property.
- CI regression gate: fail if Recall@5 declines by more than 5% relative to the checked-in baseline (relative decline), once the evaluation dataset and baseline are approved. Also fail on missing/invalid citations in answerable cases beyond the configured tolerance.
- Clear errors, bounded retries/timeouts, graceful shutdown, and reproducible migrations.
- Secrets only through environment or a secret manager; upload validation and parameterized SQL; no public unauthenticated deployment is in MVP scope.

## 7. Out of scope for MVP

Multi-tenant authorization, production SSO, distributed workers, OCR for scanned PDFs unless added as a scoped phase decision, automatic web crawling, complex query routing, semantic cache, user feedback learning, hard-negative mining, Kubernetes, and claims of production-scale throughput.

## 8. Success criteria

- A new developer can run the documented local stack and ingest sample documents.
- Repeated ingestion is idempotent and changed content replaces the active version without duplicate active chunks.
- The API and UI return citations traceable to stored source locations.
- Ablations and latency percentiles are generated from a reproducible run.
- CI runs deterministic unit/integration checks and the approved retrieval gate; expensive model-dependent jobs can be explicitly marked and provisioned.
- Measured results are recorded with dataset, model, hardware, configuration, and commit; no target is presented as an achieved result without evidence.

## 9. Decisions to confirm during Phase 0

Proceed with defaults unless repository constraints contradict them: local BGE-small embeddings (384 dimensions); configurable hosted/local answer generation; no authentication for localhost-only development; 25 MiB upload cap; English-first evaluation; default chunk size/overlap above. Record decisions and any changes in an ADR or project README.

