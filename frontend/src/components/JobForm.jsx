import { useState } from "react";
import { api } from "../api.js";

export default function JobForm({ onCreated, onError }) {
  const [mode, setMode] = useState("paste");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const job = await api.createJob(mode === "upload" ? { file } : { text });
      onCreated(job);
      setText("");
      setFile(null);
    } catch (err) {
      onError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const ready = mode === "upload" ? !!file : text.trim().length > 50;

  return (
    <section className="card">
      <h2>1 · Job description</h2>
      <p className="muted">
        Paste or upload a JD. Required skills, preferred skills, experience, education and responsibilities
        are extracted automatically.
      </p>
      <div className="tabs">
        <button className={mode === "paste" ? "on" : ""} onClick={() => setMode("paste")} type="button">Paste text</button>
        <button className={mode === "upload" ? "on" : ""} onClick={() => setMode("upload")} type="button">Upload file</button>
      </div>
      <form onSubmit={submit}>
        {mode === "paste" ? (
          <textarea value={text} onChange={(e) => setText(e.target.value)} rows={14}
                    placeholder="Senior Backend Engineer (Java)&#10;&#10;Requirements&#10;- 4+ years …" />
        ) : (
          <label className="dropzone small">
            <input type="file" accept=".pdf,.docx,.txt" onChange={(e) => setFile(e.target.files[0] || null)} />
            {file ? <b>{file.name}</b> : <span>Choose a PDF, DOCX or TXT file</span>}
          </label>
        )}
        <button className="primary" disabled={!ready || busy}>
          {busy ? "Extracting requirements…" : "Analyse job description"}
        </button>
      </form>
    </section>
  );
}
