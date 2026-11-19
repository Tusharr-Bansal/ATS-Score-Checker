const STAGE_LABEL = { queued: "queued", processing: "reading", extracted: "read", matching: "matching" };

export function scoreClass(s) {
  if (s == null) return "";
  return s >= 75 ? "s-strong" : s >= 60 ? "s-good" : s >= 40 ? "s-partial" : "s-weak";
}

const years = (c) =>
  c.total_years == null ? "—" : `${Number(c.relevant_years ?? 0).toFixed(1)} yrs relevant · ${Number(c.total_years).toFixed(1)} total`;

export default function RankingTable({ ranking, job, onSelect, selectedId }) {
  const rows = ranking.candidates;
  if (!rows.length) return null;
  const req = job?.data?.min_years;
  return (
    <section className="card">
      <div className="card-head">
        <h2>3 · Candidate ranking</h2>
        {ranking.pending > 0 && <span className="pill busy">Analysing {ranking.pending} resume(s)…</span>}
      </div>
      <table className="rank">
        <thead>
          <tr>
            <th>#</th>
            <th>Candidate</th>
            <th>Experience{req != null && <span className="muted small"> (needs {req}+)</span>}</th>
            <th>Match %</th>
            <th>Matched skills</th>
            <th>Missing</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.id} className={`${c.status !== "done" ? "dim" : "click"} ${selectedId === c.id ? "sel" : ""}`}
                onClick={() => c.status === "done" && onSelect(c.id)}>
              <td>{c.rank ?? ""}</td>
              <td>
                <div className="cand-name">{c.name}</div>
                <div className="muted small">{c.filename}</div>
              </td>
              <td>{c.status === "done" ? years(c) : ""}</td>
              <td>
                {c.status === "done" ? (
                  <div className="score-cell">
                    <span className={`score ${scoreClass(c.score)}`}>{Math.round(c.score)}%</span>
                    <span className="muted small">{c.fit}</span>
                  </div>
                ) : c.status === "error" ? (
                  <span className="err" title={c.error}>Error</span>
                ) : (
                  <span className="pill busy">{STAGE_LABEL[c.status] || c.status}</span>
                )}
              </td>
              <td className="skills-cell">
                {c.matched_skills.slice(0, 6).map((s) => <span key={s} className="chip ok">{s.split(" (or")[0]}</span>)}
                {c.matched_skills.length > 6 && <span className="muted small">+{c.matched_skills.length - 6}</span>}
              </td>
              <td className="skills-cell">
                {c.status === "error" ? <span className="muted small">{c.error}</span> :
                  c.missing_skills.slice(0, 4).map((s) => <span key={s} className="chip miss">{s.split(" (or")[0]}</span>)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted small">Click a candidate to see the full analysis.</p>
    </section>
  );
}
