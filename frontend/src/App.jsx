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
      <div className="result-card">
        <div className="result-card-title">🔍 Asset Detection</div>
        <div className="result-card-content">
          <div>Objects: {summary.objects}</div>
          {summary.detections?.map((det, i) => (
            <div key={i} style={{ fontSize: '11px', color: '#666', marginTop: '2px' }}>
              • {det.class} ({Math.round(det.confidence * 100)}%)
            </div>
          ))}
        </div>
      </div>
    )
  }
  
  if (model === 'defect_analysis') {
    const scoreColor = summary.defect_score > 0.7 ? '#dc3545' : summary.defect_score > 0.3 ? '#ffc107' : '#28a745'
    return (
      <div className="result-card">
        <div className="result-card-title">🔧 Defect Analysis</div>
        <div className="result-card-content">
          <div style={{ color: scoreColor, fontWeight: '600' }}>
            Score: {Math.round(summary.defect_score * 100)}% ({summary.defect_type})
          </div>
          <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>
            Confidence: {Math.round(summary.confidence * 100)}%
          </div>
        </div>
      </div>
    )
  }
  
  if (model === 'road_condition') {
    const conditionColor = summary.condition === 'excellent' ? '#28a745' : 
                          summary.condition === 'good' ? '#20c997' :
                          summary.condition === 'fair' ? '#ffc107' :
                          summary.condition === 'poor' ? '#fd7e14' : '#dc3545'
    return (
      <div className="result-card">
        <div className="result-card-title">🛣️ Road Condition</div>
        <div className="result-card-content">
          <div style={{ color: conditionColor, fontWeight: '600', fontSize: '14px' }}>
            {summary.condition.toUpperCase()} ({Math.round(summary.score * 100)}%)
          </div>
          <div style={{ fontSize: '11px', color: '#666', marginTop: '4px' }}>
            Surface: {summary.surface_type} | Weather: {summary.weather_impact}
          </div>
        </div>
      </div>
    )
  }
  
  if (model === 'traffic_analysis') {
    const densityColor = summary.density === 'high' ? '#dc3545' : summary.density === 'medium' ? '#ffc107' : '#28a745'
    return (
      <div className="result-card">
        <div className="result-card-title">🚗 Traffic Analysis</div>
        <div className="result-card-content">
          <div>Vehicles: {summary.vehicle_count} | Speed: {Math.round(summary.average_speed)} km/h</div>
          <div style={{ color: densityColor, fontWeight: '600', marginTop: '4px' }}>
            Density: {summary.density} | Congestion: {Math.round(summary.congestion_level * 100)}%
          </div>
        </div>
      </div>
    )
  }
  
  return null
}

function StreamRow({ s }) {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const fetchResults = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getResults(s.stream_id)
      setResults(data.results.slice(-8))
      console.log(`Updated results for ${s.stream_id}:`, data.results.length)
    } catch (err) {
      setError(err.message)
      console.error(`Failed to fetch results for ${s.stream_id}:`, err)
    } finally {
      setLoading(false)
    }
  }
  
  useInterval(fetchResults, 10000) // Auto-refresh every 10 seconds

  // Group results by model to show latest from each
  const latestResults = {}
  results.forEach(result => {
    if (!latestResults[result.model] || result.timestamp > latestResults[result.model].timestamp) {
      latestResults[result.model] = result
    }
  })

  return (
    <tr>
      <td style={{ fontWeight: '600', fontSize: '13px' }}>{s.stream_id}</td>
      <td style={{ fontSize: '12px', maxWidth: '200px', wordBreak: 'break-all' }}>{s.source}</td>
      <td style={{ fontSize: '12px' }}>{s.models.join(', ')}</td>
      <td>
        <span className={s.running ? 'status-badge status-running' : 'status-badge status-stopped'}>
          {s.running ? 'Running' : 'Stopped'}
        </span>
      </td>
      <td>
        {loading && <div className="loading-text">Loading...</div>}
        {error && <div className="error-text">Error: {error}</div>}
        <div className="result-cards">
          {Object.values(latestResults).map((result, i) => (
            <ResultCard key={i} result={result} />
          ))}
        </div>
        {results.length === 0 && !loading && !error && <div className="no-results">No results yet...</div>}
      </td>
      <td>
        <div className="action-buttons">
          <button onClick={fetchResults} disabled={loading} className="btn-refresh">
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          <button onClick={() => stopStream(s.stream_id)} className="btn-stop">
            Stop
          </button>
        </div>
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

  const handleStart = () => {
    startStream(form.id || `s-${Date.now()}`, form.source, form.models.split(',').map(s => s.trim()).filter(Boolean))
  }

  return (
    <div className="vms-container">
      <div className="vms-header">
        <h1 className="vms-title">VMS - Video Management System</h1>
        {health && <p className="vms-models">AI Models: {health.models.join(', ')}</p>}
      </div>
      
      <div className="vms-form">
        <input 
          className="vms-input"
          placeholder="Stream ID" 
          value={form.id} 
          onChange={e => setForm({...form, id: e.target.value})} 
        />
        <input 
          className="vms-input"
          placeholder="Source (0 for webcam or video path)" 
          value={form.source} 
          onChange={e => setForm({...form, source: e.target.value})} 
        />
        <input 
          className="vms-input"
          placeholder="Models (comma-separated)" 
          value={form.models} 
          onChange={e => setForm({...form, models: e.target.value})} 
        />
        <button className="vms-button" onClick={handleStart}>Start Stream</button>
      </div>

      <table className="vms-table">
        <thead>
          <tr>
            <th>Stream ID</th>
            <th>Source</th>
            <th>AI Models</th>
            <th>Status</th>
            <th>Recent Results</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {streams.map(s => <StreamRow key={s.stream_id} s={s} />)}
        </tbody>
      </table>
    </div>
  )
}

export default App
