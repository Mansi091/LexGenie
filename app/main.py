from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any
import os

from app.config import settings
from app.services.pdf_processor import extract_text_from_pdf
from app.services.contract_analyzer import analyze_contract as analyze_contract_service
from app.services.contract_chat import chat_about_contract

app = FastAPI(
    title="LexiGenie",
    description="AI-powered legal contract review system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RiskItem(BaseModel):
    clause_type: str
    section: str
    severity: str
    explanation: str
    text_found: str

class MissingClauseItem(BaseModel):
    clause_type: str
    title: str
    explanation: str
    suggested_text: str

class ContradictionItem(BaseModel):
    sections_involved: List[str]
    explanation: str

class AnalysisResponse(BaseModel):
    status: str
    contract_type: str
    risks: List[RiskItem]
    missing_clauses: List[MissingClauseItem]
    contradictions: List[ContradictionItem]
    logs: List[str]
    contract_text: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]
    contract_text: str
    analysis_report: Any = None

class ChatResponse(BaseModel):
    response: str

@app.get("/")
async def get_root():
    return {
        "message": "api is running",
        "status": "healthy"
    }

@app.post(
    "/analyze",
    response_model=AnalysisResponse
)
async def analyze_contract(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:

        file_bytes = await file.read()

        contract_text = extract_text_from_pdf(
            file_bytes
        )

        analysis_result = analyze_contract_service(
            contract_text
        )

        return AnalysisResponse(
            status="success",
            contract_type=analysis_result.get(
                "contract_type",
                "Unknown"
            ),
            risks=analysis_result.get(
                "risks",
                []
            ),
            missing_clauses=analysis_result.get(
                "missing_clauses",
                []
            ),
            contradictions=analysis_result.get(
                "contradictions",
                []
            ),
            logs=analysis_result.get(
                "logs",
                []
            ),
            contract_text=contract_text
        )

    except ValueError as ve:

        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "An error occurred during "
                f"contract review: {str(e)}"
            )
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        response_text = chat_about_contract(
            message=request.message,
            history=history_dicts,
            contract_text=request.contract_text,
            analysis_report=request.analysis_report
        )
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )
