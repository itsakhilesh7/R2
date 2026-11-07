export default function Home() {
  return (
    <main className="shell">
      <div className="eyebrow">LOCAL KNOWLEDGE WORKSPACE</div>
      <h1>Hybrid RAG</h1>
      <p className="intro">
        Your local retrieval workspace is ready for the next phase. Document ingestion and search
        will be added in their reviewed phases.
      </p>
      <section className="status-card" aria-labelledby="status-title">
        <div className="status-indicator" aria-hidden="true" />
        <div>
          <h2 id="status-title">Phase 1 scaffold</h2>
          <p>API, database, and cache services are configured for local development.</p>
        </div>
      </section>
      <footer>Runs locally · No model downloads in this phase</footer>
    </main>
  );
}
