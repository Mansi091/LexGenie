import React, { useState } from 'react'

export default function RiskTextExpander({ text }) {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <div>
      <button className="expand-button" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '▲ Hide Contract Text' : '▼ View Contract Text'}
      </button>
      {isOpen && (
        <pre className="snippet-block">
          {text}
        </pre>
      )}
    </div>
  )
}
