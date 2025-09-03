export const API_BASE = 'http://54.159.177.183';

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
  try {
    console.log(`Fetching results for stream: ${stream_id} from ${API_BASE}/results/${stream_id}`);
    const res = await fetch(`${API_BASE}/results/${stream_id}?limit=10`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    const data = await res.json();
    console.log(`Got ${data.results?.length || 0} results for ${stream_id}`);
    return data;
  } catch (error) {
    console.error(`Error fetching results for ${stream_id}:`, error);
    return { results: [] };
  }
}
