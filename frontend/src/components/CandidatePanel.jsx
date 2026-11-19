import { useEffect, useState } from "react";
import { api } from "../api.js";
import { scoreClass } from "./RankingTable.jsx";

const COMPONENTS = [
  ["skills", "Skills match", "Required (80%) + nice-to-have (20%) coverage; core skills count double"],
  ["semantic", "Semantic similarity", "Embedding similarity of resume to the JD and its responsibilities"],
  ["experience", "Relevant experience", "Relevance-weighted years vs the JD minimum"],
  ["education", "Education", "Degree level and field vs the JD"],
];
const STATUS = { matched: "✓", partial: "◐", related: "≈", missing: "✕" };
const judgedBy = (s) =>
  s.source === "llm" ? (s.status === "missing" ? "LLM" : "LLM · verified quote")
  : s.source === "llm_rejected" ? "LLM quote rejected → rules"
  : "Rules";
const fmtMonths = (m) => (m >= 12 ? `${(m / 12).toFixed(1)} yrs` : `${m} mo`);

export default function CandidatePanel({ id, onClose }) {
  const [c, setC] = useState(null);
  useEffect(() => {
    setC(null);
    api.candidate(id).then(setC);
  }, [id]);

  return (
    <div className="overlay" onClick={onClose}>
      <aside className="panel" onClick={(e) => e.stopPropagation()}>
        <button className="close" onClick={onClose}>✕</button>
        {!c ? <div className="muted">Loading…</div> : <Body c={c} />}
      </aside>
    </div>
  );
}

function Body({ c }) {
  const p = c.profile || {};
  const r = c.result;
  if (!r) return <div className="err">{c.error || "Not scored yet."}</div>;
  const b = r.breakdown;
  const e = r.experience;
  const ed = r.education;
  return (
    <>
      <header className="panel-head">
        <div className={`ring ${scoreClass(r.score)}`}>
          <span>{Math.round(r.score)}</span><small>/100</small>
        </div>
        <div>
          <h2>{p.name || c.filename}</h2>
          <div className="muted">{[p.email, p.phone, p.location].filter(Boolean).join(" · ")}</div>
          <div className={`fit ${scoreClass(r.score)}`}>{r.fit} for {c.job_title}</div>
        </div>
      </header>

      <h3>Score breakdown</h3>
      <div className="breakdown">
        {COMPONENTS.filter(([k]) => b[k]?.max_points).map(([k, label, help]) => (
          <div key={k} className="bar-row" title={help}>
            <div className="bar-label">{label}<span className="muted small">{help}</span></div>
            <div className="bar"><div style={{ width: `${(b[k].score || 0) * 100}%` }} /></div>
            <div className="bar-val">{b[k].points} / {b[k].max_points}</div>
          </div>
        ))}
      </div>

      <h3>Why this score</h3>
      <ul className="reasons">
        {r.reasons.map((x, i) => <li key={i} className={x.type}>{x.text}</li>)}
      </ul>

      <h3>Skills</h3>
      <table className="mini">
        <thead><tr><th></th><th>JD skill</th><th>Type</th><th>Evidence</th><th>Judged by</th></tr></thead>
        <tbody>
          {r.skill_details.map((s, i) => (
            <tr key={i} className={s.status}>
              <td className="st">{STATUS[s.status]}</td>
              <td>{s.core && "★ "}{s.skill}</td>
              <td className="muted small">{s.kind}</td>
              <td className="small">{s.evidence}</td>
              <td className="small muted">{judgedBy(s)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Experience comparison</h3>
      <div className="exp-cmp">
        <div><b>{e.required_years != null ? `${e.required_years}+` : "—"}</b><span>required (yrs)</span></div>
        <div><b>{e.relevant_years}</b><span>relevant (yrs)</span></div>
        <div><b>{e.total_years}</b><span>total (yrs)</span></div>
      </div>
      <table className="mini">
        <thead><tr><th>Role</th><th>Period</th><th>Duration</th><th>Relevance</th></tr></thead>
        <tbody>
          {e.entries.map((x, i) => (
            <tr key={i}>
              <td>{x.title}<div className="muted small">{x.company}{x.internship && " · internship (counts 50%)"}</div></td>
              <td className="small">{x.start || "?"} → {x.end || "?"}</td>
              <td className="small">{fmtMonths(x.months)}</td>
              <td><div className="bar thin"><div style={{ width: `${x.relevance * 100}%` }} /></div></td>
            </tr>
          ))}
        </tbody>
      </table>

      {r.responsibility_coverage?.length > 0 && (
        <>
          <h3>JD responsibilities vs resume evidence</h3>
          <table className="mini">
            <tbody>
              {r.responsibility_coverage.map((x, i) => (
                <tr key={i}>
                  <td className="small">{x.responsibility}</td>
                  <td className="small muted">{x.evidence}</td>
                  <td><div className="bar thin"><div style={{ width: `${x.strength * 100}%` }} /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h3>Extracted candidate information</h3>
      <div className="info">
        {p.summary && <p>{p.summary}</p>}
        <div className="label">Education</div>
        <ul>{(p.education || []).map((x, i) => <li key={i}>{x.degree}{x.institution && `, ${x.institution}`}{x.end_year && ` (${x.end_year})`}</li>)}</ul>
        {ed.required_level !== "none" && (
          <div className="muted small">JD asks for {ed.required_level} ({ed.required ? "required" : "preferred"}); candidate has {ed.candidate_level}.</div>
        )}
        <div className="label">All extracted skills</div>
        <div className="chips">{(p.skills || []).map((s) => <span key={s} className="chip soft">{s}</span>)}</div>
        {p.projects?.length > 0 && (<>
          <div className="label">Projects</div>
          <ul>{p.projects.map((x, i) => <li key={i}><b>{x.name}</b> — {x.description}</li>)}</ul>
        </>)}
        {p.certifications?.length > 0 && (<>
          <div className="label">Certifications</div>
          <ul>{p.certifications.map((x, i) => <li key={i}>{x}</li>)}</ul>
        </>)}
        <div className="muted small">Parsed from {c.filename} using {c.extractor === "gemini" ? "Gemini" : "rule-based extraction"}.</div>
      </div>
    </>
  );
}
