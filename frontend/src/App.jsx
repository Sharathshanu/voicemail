
import { useState } from 'react'
import axios from 'axios'
import './index.css'

function App() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null) // 'success' or 'error'
  const [statusMsg, setStatusMsg] = useState('')

  const handleSend = async (e) => {
    e.preventDefault()
    setLoading(true)
    setStatus(null)
    setStatusMsg('')

    try {
      const response = await axios.post('/api/send', {
        email,
        message
      })

      if (response.data.success) {
        setStatus('success')
        setStatusMsg('Voice message sent successfully!')
        setMessage('')
        setEmail('')
      }
    } catch (error) {
      console.error(error)
      setStatus('error')
      setStatusMsg(error.response?.data?.error || 'Failed to send message. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="card">
        <h1>Voice Messenger</h1>
        <p className="subtitle">Send text as voice, instantly.</p>

        <form onSubmit={handleSend}>
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="recipient@example.com"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="message">Message</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message here..."
              rows="4"
              required
            />
          </div>

          <button type="submit" disabled={loading} className={loading ? 'loading' : ''}>
            {loading ? 'Sending...' : 'Send Voice Message'}
          </button>

          {status && (
            <div className={`status-message ${status}`}>
              {statusMsg}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

export default App
