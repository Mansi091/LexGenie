import React from 'react'

export default function ChatbotPanel({ chatHistory, chatInput, setChatInput, chatLoading, handleSendMessage }) {
  return (
    <div className="chatbot-panel">
      <div className="chat-header">
        <h3>💬 Ask about this Contract</h3>
      </div>
      <div className="chat-messages">
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {chatLoading && (
          <div className="chat-message assistant" style={{ fontStyle: 'italic', color: 'var(--text-muted)' }}>
            AI is writing response...
          </div>
        )}
      </div>
      <form onSubmit={handleSendMessage} className="chat-input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about the contract..."
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          disabled={chatLoading}
        />
        <button type="submit" className="chat-send-btn" disabled={chatLoading || !chatInput.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}
