import { useState } from "react";
import { api } from "../api.js";

const OK = /\.(pdf|docx)$/i;

export default function ResumeUpload({ jobId, onUploaded, onError }) {
  const [files, setFiles] = useState([]);
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
      const r = await api.uploadResumes(jobId, files);
      setMsg(`${r.queued} resume(s) queued for analysis${r.rejected.length ? `, ${r.rejected.length} rejected` : ""}.`);
      setFiles([]);
      onUploaded();
    } catch (e) {
      onError(e.message);
    } finally {
      setBusy(false);
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
    </section>
  );
}
