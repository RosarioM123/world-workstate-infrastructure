import { useEffect, useState } from "react";

/**
 * Fetches /api/state and renders the materialized entities plus the
 * recent ledger. Renders nothing (beyond BackendStatus) when the
 * backend is unreachable — the page must stay useful offline.
 */
export default function StatePanel() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/state", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((json) => {
        if (!cancelled) setData(json);
      })
      .catch(() => {
        if (!cancelled) setData(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!data) return null;

  return (
    <div className="grid-3" style={{ marginBottom: 24 }}>
      <div className="card" style={{ gridColumn: "1 / -1" }}>
        <h3>entities</h3>
        <table className="state-table">
          <thead>
            <tr>
              <th>entity</th>
              <th>capacity</th>
              <th>liquidity</th>
              <th>status</th>
            </tr>
          </thead>
          <tbody>
            {data.entities.map((e) => (
              <tr key={e.entity_id}>
                <td className="mono">{e.entity_id}</td>
                <td>{e.capacity}</td>
                <td>{e.available_liquidity}</td>
                <td>{e.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card" style={{ gridColumn: "1 / -1" }}>
        <h3>recent ledger</h3>
        <table className="state-table">
          <thead>
            <tr>
              <th>#</th>
              <th>entity</th>
              <th>action</th>
              <th>verdict</th>
              <th>hash</th>
            </tr>
          </thead>
          <tbody>
            {data.recent_ledger.map((r) => (
              <tr key={r.transaction_id}>
                <td>{r.transaction_id}</td>
                <td className="mono">{r.entity_id}</td>
                <td className="mono">{r.action}</td>
                <td className={`status-${r.status}`}>{r.status}</td>
                <td className="hash mono">{r.record_hash.slice(0, 12)}…</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
