import BackendStatus from "./components/BackendStatus.jsx";
import StatePanel from "./components/StatePanel.jsx";
import "./styles.scss";

function HowItWorks() {
  const steps = [
    {
      title: "1 · intent",
      body: "An agent or human proposes a state change: an entity, an action, and deltas. Agents never write state directly.",
    },
    {
      title: "2 · constraint engine",
      body: "engine.py validates the intent against physical and financial limits. Capacity and liquidity cannot go negative; locked nodes reject everything; NaN and Infinity are refused.",
    },
    {
      title: "3 · ledger",
      body: "Every attempt — COMMITTED or REJECTED — is appended to a SHA-256 hash-chained SQLite ledger. The attempt itself is always auditable.",
    },
  ];
  return (
    <section className="block" id="how">
      <h2>How it works</h2>
      <p className="section-sub">
        A deterministic state kernel: proposals go in, verdicts come out, and
        history is replayable by anyone.
      </p>
      <div className="grid-3">
        {steps.map((s) => (
          <div className="card" key={s.title}>
            <h3>{s.title}</h3>
            <p>{s.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function ApiDocs() {
  return (
    <section className="block" id="api">
      <h2>API quickstart</h2>
      <p className="section-sub">
        Run the backend locally, then talk to it. No keys, no signup.
      </p>
      <pre className="code">
{`$ uvicorn app:app
$ curl 127.0.0.1:8000/api/state

$ curl -X POST 127.0.0.1:8000/api/intent \\
    -H "Content-Type: application/json" \\
    -d '{"entity_id":"node_rotterdam_hub","action":"ALLOCATE",
         "requested_delta_capacity":-50.0,"requested_delta_cash":0.0}'

$ curl -X POST 127.0.0.1:8000/api/rogue-attack
  # every verdict: REJECTED`}
      </pre>
    </section>
  );
}

function Limits() {
  const items = [
    <>
      <strong>Tamper-evident, not immutable.</strong> The ledger is hash-chained,
      so edits are detectable — but anyone with the database file can rewrite
      it. Verification is by <span className="mono">verify_chain()</span>, not
      by cryptography alone.
    </>,
    <>
      <strong>No auth or rate limiting yet.</strong> This is a working
      prototype; the API trusts its callers.
    </>,
    <>
      <strong>The weather mapping is a demo hypothesis.</strong> Wind speed
      derating port capacity is a fixed, auditable rule for demonstration —
      not a validated operations model.
    </>,
    <>
      <strong>Sample data is labeled.</strong> Anything synthetic in the demo
      is marked synthetic; live Open-Meteo data needs no API key.
    </>,
  ];
  return (
    <section className="block" id="limits">
      <h2>Honest limits</h2>
      <p className="section-sub">
        What this prototype is not — stated up front, not buried in a footnote.
      </p>
      <ul className="limits">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export default function App() {
  return (
    <div className="page">
      <header className="site-header">
        <div className="brand">WORLD</div>
        <nav>
          <a href="#how">How it works</a>
          <a href="#api">API</a>
          <a href="#limits">Limits</a>
          <a href="/demo">Live demo</a>
        </nav>
      </header>

      <div className="hero">
        <h1>
          Deterministic work-state
          <br />
          infrastructure.
        </h1>
        <p className="lede">
          AI can generate work. What it cannot do reliably is maintain a
          shared, verifiable record of that work as it moves between models,
          agents, humans, tools, and time. WORLD is that record.
        </p>
        <div className="cta-row">
          <a className="btn primary" href="/demo">
            Launch live demo →
          </a>
          <a
            className="btn"
            href="https://github.com/RosarioM123/world-ai-infrastructure"
          >
            GitHub
          </a>
        </div>
        <div>
          <span className="prototype-note">
            Working prototype — not yet deployed. Run it locally.
          </span>
        </div>
      </div>

      <section className="block" id="live">
        <h2>Live state</h2>
        <p className="section-sub">
          Straight from the ledger, when the backend is running.
        </p>
        <BackendStatus />
        <StatePanel />
      </section>

      <HowItWorks />
      <ApiDocs />
      <Limits />

      <footer className="site-footer">
        <span>WORLD · deterministic state kernel</span>
        <span>engine.py · app.py · ingest.py</span>
      </footer>
    </div>
  );
}
