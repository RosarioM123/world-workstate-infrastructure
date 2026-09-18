import { useEffect, useState } from "react";

/**
 * Probes /health and reports backend liveness.
 * The backend may be absent (static preview, backend not started) —
 * that is a normal state here, not an error page.
 */
export default function BackendStatus() {
  const [state, setState] = useState("checking"); // checking | ok | down

  useEffect(() => {
    let cancelled = false;
    fetch("/health", { cache: "no-store" })
      .then((r) => {
        if (!cancelled) setState(r.ok ? "ok" : "down");
      })
      .catch(() => {
        if (!cancelled) setState("down");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="status-line">
      <span className={`dot ${state === "ok" ? "ok" : state === "down" ? "bad" : ""}`} />
      {state === "checking" && <span>Probing backend…</span>}
      {state === "ok" && <span>Backend online — live ledger below.</span>}
      {state === "down" && (
        <span>
          Backend offline.{" "}
          <span className="hint">
            Run <span className="mono">uvicorn app:app</span> and reload to see live state.
          </span>
        </span>
      )}
    </div>
  );
}
