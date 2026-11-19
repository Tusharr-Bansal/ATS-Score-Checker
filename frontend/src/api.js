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
  deleteJob: (id) => request(`/api/jobs/${id}`, { method: "DELETE" }),
  createJob: ({ text, file }) => {
    const fd = new FormData();
    if (file) fd.append("file", file);
    else fd.append("text", text);
    return request("/api/jobs", { method: "POST", body: fd });
  },
  // XMLHttpRequest (not fetch) so the browser reports upload progress
  uploadResumes: (jobId, files, onProgress) =>
    new Promise((resolve, reject) => {
      const fd = new FormData();
      files.forEach((f) => fd.append("files", f));
      const xhr = new XMLHttpRequest();
      xhr.open("POST", `${BASE}/api/jobs/${jobId}/resumes`);
      xhr.upload.onprogress = (e) => e.lengthComputable && onProgress?.(e.loaded / e.total);
      xhr.onload = () => {
        let body = {};
        try { body = JSON.parse(xhr.responseText); } catch { /* non-JSON error page */ }
        xhr.status < 300 ? resolve(body) : reject(new Error(body.detail || `Upload failed (${xhr.status})`));
      };
      xhr.onerror = () => reject(new Error("Upload failed: network error"));
      xhr.send(fd);
    }),
  ranking: (jobId) => request(`/api/jobs/${jobId}/candidates`),
  candidate: (id) => request(`/api/candidates/${id}`),
};
