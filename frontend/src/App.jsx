import React, { useState } from 'react'
import RiskTextExpander from './components/RiskTextExpander'
import MissingClauseHelper from './components/MissingClauseHelper'
import ChatbotPanel from './components/ChatbotPanel'

const API_BASE = import.meta.env.DEV ? 'http://127.0.0.1:8080' : ''

export default function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [contractText, setContractText] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  const handleFileChange = async (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setLoading(true)
    setReport(null)
    setError(null)
    setContractText('')
    setChatHistory([])

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let errMsg = 'Analysis failed.'
        try {
          const errData = await response.json()
          errMsg = errData.detail || errMsg
        } catch (e) {
          errMsg = `Backend server is offline or returned an invalid response (Status: ${response.status}).`
        }
        throw new Error(errMsg)
      }

      const data = await response.json()
      setReport(data)
      setContractText(data.contract_text || '')
      setChatHistory([
        { role: 'system', content: 'You can now ask questions about the analyzed contract.' }
      ])
    } catch (err) {
      setError(err.message)
      setFile(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!chatInput.trim() || chatLoading) return

    const userMessage = { role: 'user', content: chatInput.trim() }
    const updatedHistory = [...chatHistory, userMessage]
    
    setChatHistory(updatedHistory)
    setChatInput('')
    setChatLoading(true)

    try {
      const apiHistory = updatedHistory
        .filter(msg => msg.role !== 'system')
        .map(msg => ({ role: msg.role, content: msg.content }))

      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          history: apiHistory.slice(0, -1),
          contract_text: contractText,
          analysis_report: report
        })
      })

      if (!response.ok) {
        let errMsg = 'Failed to get answer from server.'
        try {
          const errData = await response.json()
          errMsg = errData.detail || errMsg
        } catch (e) {
          errMsg = `Backend server is offline (Status: ${response.status}).`
        }
        throw new Error(errMsg)
      }

      const data = await response.json()
      setChatHistory([...updatedHistory, { role: 'assistant', content: data.response }])
    } catch (err) {
      setChatHistory([...updatedHistory, { role: 'system', content: `Error: ${err.message}` }])
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className={`container ${report ? 'has-report' : ''}`}>
      <header className="title-header">
        <h1>⚖️ Legal Contract Reviewer</h1>
        <p>Upload a contract PDF to begin.</p>
      </header>

      {/* Drag & Drop or Click Upload Area */}
      <div className="upload-box" onClick={() => document.getElementById('file-input').click()}>
        <input 
          type="file" 
          id="file-input"
          accept=".pdf" 
          onChange={handleFileChange} 
          style={{ display: 'none' }} 
        />
        <div style={{ fontSize: '3rem', marginBottom: '10px' }}>📄</div>
        <p style={{ fontWeight: '600', marginBottom: '5px', color: 'var(--text-main)' }}>
          Upload PDF
        </p>
        {file && (
          <p style={{ marginTop: '15px', color: 'var(--primary-yellow)', fontWeight: 'bold' }}>
            Uploading: {file.name}
          </p>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div style={{
          backgroundColor: '#FFFBEB',
          border: '1px solid var(--primary-yellow)',
          color: '#92400E',
          padding: '15px 20px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '25px',
          fontWeight: '500',
          boxShadow: 'var(--shadow)'
        }}>
          ⚠️ <strong>Error:</strong> {error}
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="loader-box">
          <div className="spinner"></div>
          <p style={{ color: 'var(--text-muted)', fontWeight: '500' }}>
            AI Review Agent is analyzing your contract... Please wait.
          </p>
        </div>
      )}

      {/* Review Results */}
      {report && (
        <div className="report-container">
          <div className="report-header">
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: '700', color: 'var(--text-main)' }}>Analysis Report</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px' }}>Review executed successfully</p>
            </div>
            <span className="classification-badge">{report.contract_type}</span>
          </div>

          <div className="dashboard-grid">
            {/* Left Column: Report findings */}
            <div className="report-main-content">
              {/* Stats Grid */}
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-label">Identified Risks</div>
                  <div className="stat-value">{report.risks ? report.risks.length : 0}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Missing Clauses</div>
                  <div className="stat-value">{report.missing_clauses ? report.missing_clauses.length : 0}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Contradictions</div>
                  <div className="stat-value">{report.contradictions ? report.contradictions.length : 0}</div>
                </div>
              </div>

              {/* Risks Section */}
              <h3 className="section-header">⚠️ Identified Risks</h3>
              {(!report.risks || report.risks.length === 0) ? (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', paddingLeft: '10px' }}>
                  No unfavorable clauses identified.
                </p>
              ) : (
                <div>
                  {report.risks.map((risk, idx) => (
                    <div key={idx} className="finding-card">
                      <div className="finding-title-row">
                        <span className="finding-title">{risk.section || 'General Clause'}</span>
                        <span className={`severity-pill ${(risk.severity || 'medium').toLowerCase()}`}>
                          {risk.severity || 'Medium'} Risk
                        </span>
                      </div>
                      <p className="finding-desc">{risk.explanation}</p>
                      {risk.text_found && (
                        <RiskTextExpander text={risk.text_found} />
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Missing Clauses Section */}
              <h3 className="section-header">🔍 Missing Clauses</h3>
              {(!report.missing_clauses || report.missing_clauses.length === 0) ? (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', paddingLeft: '10px' }}>
                  All standard protections are included.
                </p>
              ) : (
                <div>
                  {report.missing_clauses.map((clause, idx) => (
                    <div key={idx} className="finding-card">
                      <div className="finding-title-row">
                        <span className="finding-title">{clause.title}</span>
                        <span className="severity-pill missing">Missing</span>
                      </div>
                      <p className="finding-desc"><strong>Why it matters:</strong> {clause.explanation}</p>
                      {clause.suggested_text && (
                        <MissingClauseHelper suggestedText={clause.suggested_text} />
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Contradictions Section */}
              <h3 className="section-header">🔗 Contradictions</h3>
              {(!report.contradictions || report.contradictions.length === 0) ? (
                <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', paddingLeft: '10px' }}>
                  No internal contradictions detected.
                </p>
              ) : (
                <div>
                  {report.contradictions.map((contra, idx) => (
                    <div key={idx} className="finding-card">
                      <div className="finding-title-row">
                        <span className="finding-title">
                          Conflict: {contra.sections_involved ? contra.sections_involved.join(' ⇄ ') : 'General'}
                        </span>
                        <span className="severity-pill high">Contradiction</span>
                      </div>
                      <p className="finding-desc">{contra.explanation}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right Column: Chatbot Panel */}
            <ChatbotPanel
              chatHistory={chatHistory}
              chatInput={chatInput}
              setChatInput={setChatInput}
              chatLoading={chatLoading}
              handleSendMessage={handleSendMessage}
            />
          </div>
        </div>
      )}
    </div>
  )
}
