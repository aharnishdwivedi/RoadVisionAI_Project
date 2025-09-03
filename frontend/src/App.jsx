import { useEffect, useMemo, useState } from 'react'
import { getHealth, getStreams, startStream, stopStream, getResults } from './api'
import './App.css'

function useInterval(callback, delay) {
  useEffect(() => {
    const id = setInterval(callback, delay)
    return () => clearInterval(id)
  }, [callback, delay])
}

function ResultCard({ result }) {
  const { model, summary } = result
  
  if (model === 'asset_detection') {
    return (
      <div style={{ border: '1px solid #ddd', padding: '8px', margin: '4px', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
        <strong>🔍 Asset Detection</strong>
        <div>Objects: {summary.objects}</div>
        {summary.detections?.map((det, i) => (
          <div key={i} style={{ fontSize: '12px', color: '#666' }}>
            • {det.class} ({Math.round(det.confidence * 100)}%)
          </div>
        ))}
      </div>
    )
  }
  
  if (model === 'defect_analysis') {
    const scoreColor = summary.defect_score > 0.7 ? '#ff4444' : summary.defect_score > 0.3 ? '#ffaa00' : '#44aa44'
    return (
      <div style={{ border: '1px solid #ddd', padding: '8px', margin: '4px', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
        <strong>🔧 Defect Analysis</strong>
        <div style={{ color: scoreColor }}>
          Score: {Math.round(summary.defect_score * 100)}% ({summary.defect_type})
        </div>
        <div style={{ fontSize: '12px', color: '#666' }}>
          Confidence: {Math.round(summary.confidence * 100)}%
        </div>
      </div>
    )
  }
  
  if (model === 'road_condition') {
    const conditionColor = summary.condition === 'excellent' ? '#44aa44' : 
                          summary.condition === 'good' ? '#88aa44' :
                          summary.condition === 'fair' ? '#aaaa44' :
                          summary.condition === 'poor' ? '#aa6644' : '#aa4444'
    return (
      <div style={{ border: '1px solid #ddd', padding: '8px', margin: '4px', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
        <strong>🛣️ Road Condition</strong>
        <div style={{ color: conditionColor, fontWeight: 'bold' }}>
          {summary.condition.toUpperCase()} ({Math.round(summary.score * 100)}%)
        </div>
        <div style={{ fontSize: '12px', color: '#666' }}>
          Surface: {summary.surface_type} | Weather: {summary.weather_impact}
        </div>
      </div>
    )
  }
  
  if (model === 'traffic_analysis') {
    const densityColor = summary.density === 'high' ? '#ff4444' : summary.density === 'medium' ? '#ffaa00' : '#44aa44'
    return (
      <div style={{ border: '1px solid #ddd', padding: '8px', margin: '4px', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
        <strong>🚗 Traffic Analysis</strong>
        <div>Vehicles: {summary.vehicle_count} | Speed: {Math.round(summary.average_speed)} km/h</div>
        <div style={{ color: densityColor }}>
          Density: {summary.density} | Congestion: {Math.round(summary.congestion_level * 100)}%
        </div>
      </div>
    )
  }
  
  return null
}

function StreamRow({ s }) {
  const [results, setResults] = useState([])
  useInterval(async () => {
    const data = await getResults(s.stream_id)
    setResults(data.results.slice(-8))
  }, 5000)

  // Group results by model to show latest from each
  const latestResults = {}
  results.forEach(result => {
    if (!latestResults[result.model] || result.timestamp > latestResults[result.model].timestamp) {
      latestResults[result.model] = result
    }
  })

  return (
    <tr>
      <td>{s.stream_id}</td>
      <td>{s.source}</td>
      <td>{s.models.join(', ')}</td>
      <td>{s.running ? 'Yes' : 'No'}</td>
      <td style={{ maxWidth: '400px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
          {Object.values(latestResults).map((result, i) => (
            <ResultCard key={i} result={result} />
          ))}
        </div>
        {results.length === 0 && <div style={{ color: '#999', fontStyle: 'italic' }}>No results yet...</div>}
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
