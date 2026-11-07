# Project Rules

These are implementation constraints for every contributor and coding agent.

## Correctness

1. Keep retrieval, ingestion, model providers, storage, and HTTP layers separated behind small interfaces.
2. Make ingestion deterministic and idempotent. A failed new version must not replace a working active version.
3. Preserve provenance from source to chunk to citation. Every citation must resolve to evidence actually supplied to the answer model.
4. Make ranking deterministic for equal scores with stable tie-breaks. Keep retrieval-only mode available for debugging.
5. Expose degraded operation explicitly. Never label lexical ranking “BM25” unless actual BM25 scoring is implemented; describe PostgreSQL FTS as BM25-style lexical retrieval.
6. Keep model names, dimensions, thresholds, chunk parameters, candidate counts, timeouts, and cache TTLs configurable and versioned.

## Security and privacy

1. Never commit secrets, real `.env` files, credentials, or private corpus content.
2. Validate uploads, constrain size and parsing time, use safe filenames, and parameterize all database operations.
3. Treat ingested text as untrusted. It cannot change system policy, trigger tools, or establish its own citation validity.
4. Do not log full source text, credentials, or full prompts by default. Redact metadata and provider errors.
5. Default to localhost development. Do not advertise an internet-facing deployment as secure without authentication, TLS, abuse controls, and a review.

## Engineering

1. Follow existing repository conventions after inspecting them. Avoid broad rewrites and unrelated dependencies.
2. Add migrations for schema changes; do not rely on implicit startup table creation outside disposable tests.
3. Use bounded timeouts, retries, batch sizes, and concurrency for external/model calls.
4. Keep API models documented and errors stable. Do not leak internal exception text to clients.
5. Add tests for changed behavior: unit tests for pure logic, integration tests for DB/search paths, and deterministic fixtures where possible.
6. Do not silently skip a failed check. Report environment-dependent checks and the reason they could not run.
7. Keep Docker images reproducible, pin compatible major versions, and avoid baking secrets or corpus data into images.
8. Update docs and `.env.example` when configuration or behavior changes.

## Measurement and claims

1. Treat all performance and quality values as targets until a reproducible benchmark records them.
2. Report dataset version, corpus size, models, hardware, configuration, commit, warm/cold state, and sample count with metrics.
3. Evaluate BM25/FTS, dense, hybrid, and reranked hybrid independently. Do not tune against the hidden test set or report only favorable slices.
4. Use the approved baseline and documented relative regression formula for CI. Do not weaken a gate to make a failing build green without recording the decision.
5. Do not claim “production-ready,” “secure,” or measured resume-bullet results without evidence.

