# ⚖️ Legal Document Analyzer

An AI-powered web application designed to analyze legal contracts, detect risks, identify missing clauses, find internal contradictions, and chat about your document.

## 🌟 Key Features
* **Contradiction Detection**: Cross-references sections to identify internal conflicts.
* **Missing Clause Helper**: Detects missing protections and generates suggested boilerplate.
* **Dual-Context Chat**: Interactive chatbot aware of the contract and analysis results.
* **API Optimized**: Uses single-pass structured extraction and truncation to minimize token costs.

## 🛠️ Tech Stack
* **Backend**: FastAPI (Python), LangChain, pdfplumber
* **LLM Engine**: Groq Cloud (Llama 3.1 8B)
* **Frontend**: React.js (Vite), Vanilla CSS

## 🏃 How to Run

### 1. Run the Backend API
From the root folder:
```bash
uv run uvicorn app.main:app --port 8080 --reload
```

### 2. Run the Frontend Dashboard
From the `frontend` folder:
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.
