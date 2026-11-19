const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || `Request failed (${res.status})`);
  return body;
}

export const api = {
  health: () => request("/api/health"),
  listJobs: () => request("/api/jobs"),
  getJob: (id) => request(`/api/jobs/${id}`),
  createJob: ({ text, file }) => {
    const fd = new FormData();
    if (file) fd.append("file", file);
    else fd.append("text", text);
    return request("/api/jobs", { method: "POST", body: fd });
  },
  uploadResumes: (jobId, files) => {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    return request(`/api/jobs/${jobId}/resumes`, { method: "POST", body: fd });
  },
  ranking: (jobId) => request(`/api/jobs/${jobId}/candidates`),
  candidate: (id) => request(`/api/candidates/${id}`),
};
