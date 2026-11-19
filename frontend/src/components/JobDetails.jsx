import { useState } from "react";

const skillLabel = (s) => s.name + (s.alternatives?.length ? ` / ${s.alternatives.join(" / ")}` : "");

export default function JobDetails({ job }) {
  const [open, setOpen] = useState(false);
  const d = job.data;
  return (
    <section className="card">
      <div className="card-head">
        <div>
          <h2>{job.title}</h2>
          <div className="muted small">
            Extracted with {job.extractor === "gemini" ? "Gemini" : "rule-based parser"}
          </div>
        </div>
        <button className="link" onClick={() => setOpen(!open)}>{open ? "Hide" : "Show"} JD text</button>
      </div>

      <div className="req-grid">
        <div>
          <div className="label">Required skills <span className="muted small">(★ = core, counts double)</span></div>
          <div className="chips">
            {d.required_skills.map((s) => (
              <span key={s.name} className={`chip ${s.core ? "core" : ""}`}>{s.core && "★ "}{skillLabel(s)}</span>
            ))}
          </div>
        </div>
        <div>
          <div className="label">Nice to have</div>
          <div className="chips">
            {d.preferred_skills.length ? d.preferred_skills.map((s) => (
              <span key={s.name} className="chip soft">{skillLabel(s)}</span>
            )) : <span className="muted">—</span>}
          </div>
        </div>
        <div className="facts">
          <div><span className="label">Experience</span> {d.min_years != null ? `${d.min_years}+ years` : "Not specified"}</div>
          <div>
            <span className="label">Education</span>{" "}
            {d.education_level === "none" ? "Not specified" :
              `${d.education_level[0].toUpperCase() + d.education_level.slice(1)}'s ${d.education_required ? "(required)" : "(preferred)"}`}
            {d.education_fields?.length > 0 && <span className="muted"> · {d.education_fields.join(", ")}</span>}
          </div>
        </div>
      </div>

      {d.responsibilities?.length > 0 && (
        <details className="resp">
          <summary>{d.responsibilities.length} responsibilities</summary>
          <ul>{d.responsibilities.map((r, i) => <li key={i}>{r}</li>)}</ul>
        </details>
      )}
      {open && <pre className="jd-text">{job.raw_text}</pre>}
    </section>
  );
}
