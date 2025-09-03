import { useEffect, useMemo, useState } from 'react'
import { getHealth, getStreams, startStream, stopStream, getResults } from './api'
import './App.css'

function useInterval(callback, delay) {
  useEffect(() => {
    const id = setInterval(callback, delay)
    return () => clearInterval(id)
  }, [callback, delay])
}

function StreamRow({ s }) {
  const [results, setResults] = useState([])
  useInterval(async () => {
    const data = await getResults(s.stream_id)
    setResults(data.results.slice(-5))
  }, 2000)

  return (
    <tr>
      <td>{s.stream_id}</td>
      <td>{s.source}</td>
      <td>{s.models.join(', ')}</td>
      <td>{s.running ? 'Yes' : 'No'}</td>
      <td>
        <pre style={{ margin: 0, maxWidth: 360, whiteSpace: 'pre-wrap' }}>{JSON.stringify(results, null, 2)}</pre>
      </td>
      <td>
        <button onClick={() => stopStream(s.stream_id)}>Stop</button>
      </td>
    </tr>
  )
}

function App() {
  const [health, setHealth] = useState(null)
  const [streams, setStreams] = useState([])
  const [form, setForm] = useState({ id: '', source: '0', models: 'asset_detection,defect_analysis' })

  useEffect(() => {
    getHealth().then(setHealth)
  }, [])

  useInterval(async () => {
    const data = await getStreams()
    setStreams(data.streams)
  }, 1500)

  const modelOptions = useMemo(() => health?.models || [], [health])

  return (
    <div style={{ padding: 16 }}>
      <h2>Video Management System</h2>
      <div style={{ marginBottom: 16 }}>
        <strong>Models:</strong> {modelOptions.join(', ')}
      </div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input placeholder='stream id' value={form.id} onChange={e => setForm({ ...form, id: e.target.value })} />
        <input placeholder='source (path/rtsp/cam index)' value={form.source} onChange={e => setForm({ ...form, source: e.target.value })} />
        <input placeholder='models comma separated' value={form.models} onChange={e => setForm({ ...form, models: e.target.value })} />
        <button onClick={() => startStream(form.id || `s-${Date.now()}`, form.source, form.models.split(',').map(s => s.trim()).filter(Boolean))}>Start</button>
      </div>

      <table border='1' cellPadding='6'>
        <thead>
          <tr>
            <th>ID</th>
            <th>Source</th>
            <th>Models</th>
            <th>Running</th>
            <th>Recent Results</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {streams.map(s => (
            <StreamRow key={s.stream_id} s={s} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App
