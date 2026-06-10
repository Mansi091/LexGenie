# ⚖️ Legal Document Analyzer

An AI-powered web application designed to analyze legal contracts, detect potential risks, identify missing clauses, find internal contradictions, and allow you to ask questions about the document through an interactive chatbot.

## 🚀 Features
* **AI Contract Review**: Automatically classifies contract types and scans them for risks (unfavorable liability caps, renewal traps, etc.).
* **Contradiction Detection**: Flags internal conflicting terms within the document.
* **Missing Clause Helper**: Recommends standard boilerplate clauses that are missing from your contract.
* **Interactive AI Chatbot**: Ask questions about the uploaded contract and get instant, context-aware answers.

## 🛠️ Tech Stack
* **Backend**: FastAPI, LangChain, Groq LLM (Llama 3)
* **Frontend**: React (Vite), Vanilla CSS

---

## 🏃 How to Run the Project

### 1. Run the Backend API
From the root folder:
```bash
# Start FastAPI backend
uv run uvicorn app.main:app --port 8080 --reload
```

### 2. Run the Frontend Dashboard
From the `frontend` folder:
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.
