# Evaluation Plan

## Purpose

Measure whether hybrid retrieval and reranking improve retrieval and whether answers are supported by evidence. Make benchmark results reproducible and prevent material retrieval regressions.

## Dataset

- Maintain at least 80 reviewed questions in versioned JSON or JSONL conforming to `eval-schema.json`.
- Include a balanced mix: exact section/error/ticker identifiers; paraphrases and semantic matches; multi-hop questions; answerable and unanswerable questions; short and long documents.
- Each answerable query must identify relevant chunk IDs after corpus ingestion, or evidence spans that the harness resolves to chunk IDs. Unanswerable questions must have an empty relevant set and an explicit `answerable: false`.
- Split development and held-out test questions. Tune thresholds on development only. Freeze and version the test split.
- Exclude private or copyrighted source material unless permitted; include corpus and dataset licenses/provenance.

## Retrieval metrics

- Recall@5 and Recall@10: fraction of queries with at least one relevant chunk in top k; also report mean per-query recall when multiple relevant chunks are labeled.
- MRR@10: reciprocal rank of first relevant chunk.
- nDCG@10: graded ranking quality where labels support graded relevance; otherwise use binary relevance and document it.
- Report answerable and exact-identifier slices separately, plus aggregate and per-query results.
- Compare four configurations on the same candidates/corpus: PostgreSQL FTS lexical, dense, RRF hybrid, hybrid + cross-encoder rerank.

## Answer and citation checks

- Citation validity: every citation ID exists among supplied evidence and every cited location matches stored provenance.
- Evidence coverage: human-reviewed rubric or a clearly documented model-assisted judge, with judge model/prompt/version and sampled human audit.
- Correctness and faithfulness: report separately; judge-supported metrics are not ground truth. Include a small human-reviewed sample for each release baseline.
- Abstention: precision/recall on unanswerable and insufficient-evidence queries. Calibrate thresholds on development data.

## Latency and cache

- Record per-stage timings for query embedding, FTS, dense query, fusion, rerank, generation, and total request.
- Report p50/p95 and sample count, warm/cold state, machine/hardware, model/provider versions, corpus/chunk counts, configuration, and commit.
- Measure cache-off, cold-cache, and warm-cache separately. Do not combine model download/startup time with steady-state request latency without labeling it.
- Initial targets: retrieval p50 ≤ 500 ms, p95 ≤ 1,500 ms on a declared local reference machine and corpus up to 10k chunks; full answer target p50 ≤ 4 s and p95 ≤ 10 s under a named generator. Treat these as targets, not results.

## CI regression policy

1. CI validates dataset schema and runs deterministic unit/integration checks on every change.
2. Model-dependent evaluation runs where required models/services are provisioned; do not silently skip it. If unavailable, mark the job blocked/optional explicitly.
3. Store a baseline artifact with dataset hash, corpus version, model versions, hardware/runtime, config, and commit.
4. Fail if Recall@5 relative decline exceeds 5%: `(baseline - current) / max(abs(baseline), epsilon) > 0.05`. For a zero baseline, use a documented absolute rule instead.
5. Also fail on citation validity regressions beyond the approved tolerance. Review metric variance before updating the baseline.
6. Baseline updates require a reason and comparison report; never update the baseline automatically from the current run.

## Reproducibility checklist

- Dataset and corpus hashes recorded
- Parser, chunker, embedding, reranker, generator, and prompt versions recorded
- Top-k, RRF k, HNSW settings, thresholds, and cache state recorded
- Random seeds and deterministic tie-break behavior documented
- Machine/OS, dependency lockfile, run date, commit, and sample count recorded
- Aggregate and slice metrics plus per-query failures saved as artifacts

