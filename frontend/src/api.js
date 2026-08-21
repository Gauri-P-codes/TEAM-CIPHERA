const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function fetchMeta() {
  const res = await fetch(`${API_BASE}/api/meta`);
  if (!res.ok) throw new Error("Failed to load form metadata");
  return res.json();
}

export async function postEstimate(payload) {
  const res = await fetch(`${API_BASE}/api/estimate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}
