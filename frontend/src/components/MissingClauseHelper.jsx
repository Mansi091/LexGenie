import React, { useState } from 'react'

export default function MissingClauseHelper({ suggestedText }) {
  const [isOpen, setIsOpen] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleCopy = (e) => {
    e.stopPropagation()
    navigator.clipboard.writeText(suggestedText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div>
      <button className="expand-button" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '▲ Hide Recommended Clause' : '▼ View Recommended Clause'}
      </button>
      {isOpen && (
        <div className="insert-container">
          <div className="insert-header">
            <span>SUGGESTED INSERTION</span>
            <button className="copy-button" onClick={handleCopy}>
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <pre className="snippet-block" style={{ whiteSpace: 'pre-wrap', marginTop: '0' }}>
            {suggestedText}
          </pre>
        </div>
      )}
    </div>
  )
}
