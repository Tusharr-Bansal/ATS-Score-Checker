import { useState } from "react";
import { api } from "../api.js";

const OK = /\.(pdf|docx)$/i;

// how far along each resume is (0..1), by its processing stage
const STAGE = { queued: 0, processing: 0.15, extracted: 0.5, matching: 0.6, done: 1, error: 1 };

function analysisProgress(ranking, batchIds) {
  if (!ranking || !batchIds.length) return null;
  const ids = new Set(batchIds);
  const rows = ranking.candidates.filter((c) => ids.has(c.id));
  if (!rows.length) return null;
  const frac = rows.reduce((s, c) => s + (STAGE[c.status] ?? 0), 0) / rows.length;
  const read = rows.filter((c) => STAGE[c.status] >= 0.5).length;
  const finished = rows.filter((c) => c.status === "done" || c.status === "error").length;
  let label;
  if (finished === rows.length) label = `Done: ${rows.filter((c) => c.status === "done").length} of ${rows.length} resumes scored`;
  else if (read < rows.length) label = `Reading resumes with AI: ${read} of ${rows.length}`;
  else label = `Matching skills and scoring: ${finished} of ${rows.length}`;
  return { frac, label, finished: finished === rows.length };
}

function Bar({ frac, label }) {
  return (
    <div className="progress">
      <div className="progress-track"><div className="progress-fill" style={{ width: `${Math.round(frac * 100)}%` }} /></div>
      <div className="progress-label">{label} <span className="muted">· {Math.round(frac * 100)}%</span></div>
    </div>
  );
}

export default function ResumeUpload({ jobId, onUploaded, onError, ranking, batchIds = [] }) {
  const [files, setFiles] = useState([]);
  const [uploadFrac, setUploadFrac] = useState(null); // 0..1 while uploading
  const [busy, setBusy] = useState(false);
  const [drag, setDrag] = useState(false);
  const [msg, setMsg] = useState("");

  const add = (list) => {
    const incoming = Array.from(list);
    const bad = incoming.filter((f) => !OK.test(f.name));
    if (bad.length) onError(`Skipped ${bad.map((f) => f.name).join(", ")} — only PDF and DOCX are supported.`);
    setFiles((prev) => {
      const names = new Set(prev.map((f) => f.name));
      return [...prev, ...incoming.filter((f) => OK.test(f.name) && !names.has(f.name))];
    });
  };

  const upload = async () => {
    setBusy(true);
    setMsg("");
    try {
      setUploadFrac(0);
      const r = await api.uploadResumes(jobId, files, setUploadFrac);
      setMsg(`${r.queued} resume(s) queued for analysis${r.rejected.length ? `, ${r.rejected.length} rejected` : ""}.`);
      setFiles([]);
      onUploaded(r.candidate_ids);
    } catch (e) {
      onError(e.message);
    } finally {
      setBusy(false);
      setUploadFrac(null);
    }
  };

  return (
    <section className="card">
      <h2>2 · Upload resumes</h2>
      <label
        className={`dropzone ${drag ? "drag" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => { e.preventDefault(); setDrag(false); add(e.dataTransfer.files); }}
      >
        <input type="file" multiple accept=".pdf,.docx" onChange={(e) => { add(e.target.files); e.target.value = ""; }} />
        <span>Drop PDF / DOCX resumes here, or click to choose. Batches of 10+ files are fine.</span>
      </label>
      {files.length > 0 && (
        <div className="file-list">
          {files.map((f) => (
            <span key={f.name} className="chip soft">
              {f.name}
              <button className="x" onClick={() => setFiles(files.filter((x) => x !== f))}>×</button>
            </span>
          ))}
        </div>
      )}
      <div className="row">
        <button className="primary" disabled={!files.length || busy} onClick={upload}>
          {busy ? "Uploading…" : `Analyse ${files.length || ""} resume${files.length === 1 ? "" : "s"}`}
        </button>
        {msg && <span className="muted">{msg}</span>}
      </div>
      {uploadFrac != null && <Bar frac={uploadFrac} label={uploadFrac < 1 ? "Uploading files" : "Upload complete, starting analysis"} />}
      {uploadFrac == null && (() => {
        const p = analysisProgress(ranking, batchIds);
        return p && <Bar frac={p.frac} label={p.label} />;
      })()}
    </section>
  );
}
