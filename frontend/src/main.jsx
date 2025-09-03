import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Minimal global fetch error logging for demo visibility
const originalFetch = window.fetch
window.fetch = async (...args) => {
  const res = await originalFetch(...args)
  if (!res.ok) {
    console.error('API error', res.status, res.statusText, args[0])
  }
  return res
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
