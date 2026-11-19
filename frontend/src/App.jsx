import { useEffect, useState } from "react";
import { api } from "./api.js";
import { OWNER } from "./owner.js";
import JobForm from "./components/JobForm.jsx";
import JobDetails from "./components/JobDetails.jsx";
import ResumeUpload from "./components/ResumeUpload.jsx";
import RankingTable from "./components/RankingTable.jsx";
import CandidatePanel from "./components/CandidatePanel.jsx";

export default function App() {
  const [health, setHealth] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [jobId, setJobId] = useState(null); // null = "new job" screen
  const [job, setJob] = useState(null);
  const [ranking, setRanking] = useState(null);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  const refreshJobs = () => api.listJobs().then(setJobs).catch((e) => setError(e.message));

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "down" }));
    refreshJobs();
  }, []);

  useEffect(() => {
    setJob(null);
    setRanking(null);
    setSelected(null);
    if (jobId == null) return;
    api.getJob(jobId).then(setJob).catch((e) => setError(e.message));
    api.ranking(jobId).then(setRanking).catch((e) => setError(e.message));
  }, [jobId]);

  // Poll the ranking while resumes are still being processed.
  useEffect(() => {
    if (!jobId || !ranking || ranking.pending === 0) return;
    const t = setTimeout(() => api.ranking(jobId).then((r) => {
      setRanking(r);
      if (r.pending === 0) refreshJobs();
    }), 2000);
    return () => clearTimeout(t);
  }, [jobId, ranking]);

  const onJobCreated = (j) => {
    refreshJobs();
    setJobId(j.id);
  };

  const onUploaded = () => api.ranking(jobId).then(setRanking);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="logo">◎</span> CheckRes
        </div>
        <button className={`new-job ${jobId == null ? "active" : ""}`} onClick={() => setJobId(null)}>
          + New job description
        </button>
        <div className="side-label">Jobs</div>
        <ul className="job-list">
          {jobs.map((j) => (
            <li key={j.id} className={j.id === jobId ? "active" : ""} onClick={() => setJobId(j.id)}>
              <div className="job-title">{j.title}</div>
              <div className="job-meta">{j.candidate_count} candidates</div>
            </li>
          ))}
          {jobs.length === 0 && <li className="empty">No jobs yet</li>}
        </ul>
        <div className="owner">
          <div>Built by <b>{OWNER.name}</b></div>
          <div className="owner-links">
            <a href={OWNER.github} target="_blank" rel="noreferrer">GitHub</a>
            <span>·</span>
            <a href={`mailto:${OWNER.email}`}>Email</a>
          </div>
        </div>
        {health && (
          <div className="engine">
            {health.status === "down" ? (
              <span className="bad">API unreachable</span>
            ) : (
              <>
                <div>Extraction: <b>{health.extractor === "gemini" ? health.llm_model : "rule-based"}</b></div>
                <div>Embeddings: <b>{health.embedding_provider}</b></div>
              </>
            )}
          </div>
        )}
      </aside>

      <main className="main">
        <div className="demo-banner">
          <b>Demo</b> · Built by {OWNER.name} as a project demonstration. Uses synthetic sample resumes and
          free-tier hosting, so the first request after a quiet period can take up to a minute.
          Please don't upload real people's resumes.{" "}
          <a href={OWNER.github} target="_blank" rel="noreferrer">Source on GitHub</a> ·{" "}
          <a href={`mailto:${OWNER.email}`}>{OWNER.email}</a>
        </div>
        {error && <div className="alert" onClick={() => setError("")}>{error} ✕</div>}
        {jobId == null ? (
          <JobForm onCreated={onJobCreated} onError={setError} />
        ) : (
          job ? (
            // resume upload only appears once the role has been analysed and its requirements are shown
            <>
              <JobDetails job={job} />
              <ResumeUpload jobId={jobId} onUploaded={onUploaded} onError={setError} />
              {ranking && <RankingTable ranking={ranking} job={job} onSelect={setSelected} selectedId={selected} />}
            </>
          ) : (
            <section className="card muted">Loading the role analysis… (the free server can take up to a minute to wake up)</section>
          )
        )}
      </main>

      {selected && <CandidatePanel id={selected} job={job} onClose={() => setSelected(null)} />}
    </div>
  );
}
