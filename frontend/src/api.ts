export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function getStreams() {
  const res = await fetch(`${API_BASE}/streams`);
  return res.json();
}

export async function startStream(stream_id: string, source: string, models: string[]) {
  const res = await fetch(`${API_BASE}/streams/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ config: { stream_id, source, models, enabled: true } }),
  });
  return res.json();
}

export async function stopStream(stream_id: string) {
  const res = await fetch(`${API_BASE}/streams/stop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stream_id }),
  });
  return res.json();
}

export async function getResults(stream_id: string) {
  const res = await fetch(`${API_BASE}/results/${stream_id}`);
  return res.json();
}
