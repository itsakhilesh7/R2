# ADR 0001: Phase 0 project decisions

- **Status:** Accepted
- **Date:** 2026-11-07
- **Scope:** Phase 0 decisions only; no application scaffolding or implementation.

## Context

The starter pack describes a local-first hybrid RAG MVP but contains no application code or runtime-specific constraints. Phase 0 needs explicit decisions for ingestion identity, lexical terminology, embedding compatibility, chunk sizing, evaluation labels, and the collaboration boundary before implementation begins.

## Decisions

### Ingestion identity and hashes

Use stable source identity plus SHA-256 of raw source bytes and matching parser, chunker, and embedding pipeline versions to decide whether an ingestion is an unchanged no-op. Store a second SHA-256 over normalized extracted text for diagnostics and reproducibility. A changed source creates a new version; activation remains atomic so a failed attempt does not displace the current active version.

### Lexical retrieval naming

Use “FTS” or “BM25-style lexical retrieval” for PostgreSQL full-text search. Do not call its ranking BM25 unless actual BM25 scoring is implemented.

### Embedding model and dimensions

Retain `BAAI/bge-small-en-v1.5` at 384 dimensions as the default. A change to embedding dimensions requires a database migration and full re-embedding. Track model and dimension changes, alternatives, and migration/re-embedding impact in an ADR.

### Chunk size and model input limits

Use 400 embedding-tokenizer tokens as the initial chunk-size default, configurable in a 350–400-token range, retaining the documented 100-token overlap unless evaluation justifies a change. Chunk size is an evaluation ablation axis.

The official Hugging Face model cards report a 512-token sequence length for `BAAI/bge-small-en-v1.5` and `BAAI/bge-reranker-base` ([embedding model card](https://huggingface.co/BAAI/bge-small-en-v1.5), [reranker model card](https://huggingface.co/BAAI/bge-reranker-base)). Token counting must use the corresponding model tokenizer. Add automated checks that chunks fit the embedding model limit and that reranker inputs, including the query and pair formatting/special tokens, fit the reranker limit. A chunk under 512 tokens by itself does not guarantee a query-plus-chunk pair fits; enforce a query budget or deterministic truncation/rejection policy without silently treating truncated evidence as complete.

### Evaluation evidence labels

Evaluation cases store stable source identity and an evidence quote/span rather than raw chunk IDs. The harness resolves each source/span against the currently ingested corpus to identify relevant chunk IDs at run time. Preserve source/corpus versioning so resolution can be audited and benchmark runs reproduced.

### Collaboration and phase gates

Codex scaffolds Docker, UI, and general boilerplate. The user hand-writes chunking, ingestion activation, RRF, and evaluation metrics; Codex reviews that code. At every phase gate, before moving to the next phase, Codex asks the user to explain 2–3 design decisions in the completed work. Work remains phase-scoped and stops at review boundaries.

## Deferred inputs

These values remain explicitly unresolved until supplied by the user:

- Sample corpus: TBD
- Reference machine: CPU / RAM / GPU TBD
- Phase 4 generator: Ollama model or free API TBD

No corpus-dependent quality or hardware-dependent latency claim is valid until these inputs are selected and a reproducible evaluation is run.

## Consequences

- Chunk boundaries are defined by the embedding tokenizer; evaluation must include 350-, 375-, and 400-token settings (or a documented equivalent) to measure the chunk-size tradeoff.
- Reranking must guard the full query-passage pair limit, not only passage length.
- Evaluation labels remain portable across rechunking, while runtime resolution and corpus version must be recorded for reproducibility.
- The initially scaffolded config/docs must use the new chunk default and must not mislabel PostgreSQL FTS as BM25.
- The remaining corpus, machine, and generator choices are not blockers for this decision record, but must be resolved before the corresponding evaluation and answer-generation work.

## References

- [BAAI/bge-small-en-v1.5 model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- [BAAI/bge-reranker-base model card](https://huggingface.co/BAAI/bge-reranker-base)
- Project requirements: `prd.md`, `architecture.md`, `phases.md`, `rules.md`, `agent-workflow.md`
