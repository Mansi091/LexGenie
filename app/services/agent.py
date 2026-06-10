import json
import logging
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings

logger = logging.getLogger(__name__)

def get_llm(api_key: str = None):
    """Initializes and returns the ChatGroq LLM instance using config or user-input key."""
    key = api_key or settings.GROQ_API_KEY
    if key and key.strip() != "":
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=key,
            temperature=0.1
        )
    return None

def analyze_contract_agent(contract_text: str, user_api_key: str = None) -> Dict[str, Any]:
    """Analyzes the contract text using a single direct LLM query."""
    logs = []
    logs.append("Received contract text for analysis.")

    llm_instance = get_llm(user_api_key)
    if not llm_instance:
        # Fallback Mock Data for Demo/Simulated Mode
        logs.append("No Groq API Key found. Operating in Demo/Mock Mode.")
        logs.append("Classified contract: SaaS Vendor Subscription Agreement (Demo)")
        logs.append("Running contract review simulations...")
        logs.append("Review complete. Report formatted successfully.")
        return {
            "contract_type": "SaaS Vendor Subscription Agreement",
            "risks": [
                {
                    "clause_type": "limitation_of_liability",
                    "section": "10. Limitation of Liability",
                    "severity": "High",
                    "explanation": "Caps vendor's liability at $5,000, which is extremely low for SaaS subscriptions.",
                    "text_found": "Vendor's total liability under this Agreement shall not exceed $5,000 under any circumstances."
                },
                {
                    "clause_type": "termination_and_renewal",
                    "section": "Clause 8. Term & Renewal",
                    "severity": "Medium",
                    "explanation": "Requires a 90-day prior written notice to prevent auto-renewal, which is an industry renewal trap.",
                    "text_found": "This Agreement will automatically renew for successive 12-month periods unless either party provides written notice of non-renewal at least 90 days prior..."
                }
            ],
            "missing_clauses": [
                {
                    "clause_type": "confidentiality",
                    "title": "Confidentiality Obligations",
                    "explanation": "Standard mutual confidentiality protections are missing from the agreement.",
                    "suggested_text": "Each party agrees to protect the other's Confidential Information with the same degree of care it uses for its own confidential info, but not less than reasonable care."
                }
            ],
            "contradictions": [
                {
                    "sections_involved": ["Section 5. IP Rights", "Section 10. Limitation of Liability"],
                    "explanation": "Section 5 specifies unlimited IP indemnification, but Section 10 caps total liability at $5,000, creating a conflict."
                }
            ],
            "logs": logs
        }

    # Live Mode
    logs.append("Groq API connection established. Initializing live analysis...")

    # Truncate contract text if it is excessively long to prevent token rate limits (TPM: 6000)
    max_char_limit = 12000
    safe_contract_text = contract_text
    if len(contract_text) > max_char_limit:
        logs.append(f"Contract text length ({len(contract_text)} chars) exceeds safety limits. Truncating to {max_char_limit} chars for API compliance.")
        safe_contract_text = contract_text[:max_char_limit] + "\n\n... [Remaining text truncated to fit API token limits] ..."

    system_prompt = (
        "You are an expert legal AI assistant specializing in contract review.\n"
        "Analyze the provided contract text and perform the following reviews:\n"
        "1. Classify the contract type (e.g. SaaS Agreement, NDA, Services Agreement).\n"
        "2. Identify potential high or medium risks (e.g. unfavorable liability caps, automatic renewal terms, harsh termination clauses).\n"
        "3. Identify critical missing clauses that should be included for standard buyer/customer protection.\n"
        "4. Detect any internal contradictions or conflicts in the text (e.g. unlimited IP indemnity vs a low overall liability cap).\n\n"
        "You MUST return your analysis ONLY as a raw JSON object matching the following structure:\n"
        "{\n"
        '  "contract_type": "string",\n'
        '  "risks": [\n'
        "    {\n"
        '      "clause_type": "string (e.g. limitation_of_liability, termination, renewal)",\n'
        '      "section": "string (name/number of section, e.g. Section 10)",\n'
        '      "severity": "string (High, Medium, or Low)",\n'
        '      "explanation": "string detailing the risk",\n'
        '      "text_found": "string containing the exact/excerpt of text from the contract"\n'
        "    }\n"
        "  ],\n"
        '  "missing_clauses": [\n'
        "    {\n"
        '      "clause_type": "string (e.g. confidentiality, data_privacy, governing_law)",\n'
        '      "title": "string title",\n'
        '      "explanation": "string explaining why it is missing and why it matters",\n'
        '      "suggested_text": "string containing proposed legal language to insert"\n'
        "    }\n"
        "  ],\n"
        '  "contradictions": [\n'
        "    {\n"
        '      "sections_involved": ["string (section name)", "string (section name)"],\n'
        '      "explanation": "string explaining the conflict"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Do not include any chat prefix, suffix, markdown wrapper (like ```json), or extra text outside the JSON object itself."
    )

    user_prompt = f"Contract text to review:\n\n{safe_contract_text}"

    try:
        logs.append("Sending contract text to LLM for comprehensive review...")
        response = llm_instance.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        response_text = response.content.strip()
        # Clean markdown wrappers if any
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        logs.append("Parsing analysis results from LLM...")
        parsed_result = json.loads(response_text)
        parsed_result["logs"] = logs + ["Analysis parsing complete. Review successfully generated."]
        return parsed_result

    except Exception as e:
        logger.error(f"Error in direct LLM analysis: {e}")
        logs.append(f"Analysis failed with error: {str(e)}")
        # Return empty response structured correctly to prevent front-end crashes
        return {
            "contract_type": "Unknown",
            "risks": [],
            "missing_clauses": [
                {
                    "clause_type": "error",
                    "title": "Analysis Error",
                    "explanation": f"The AI analysis pipeline encountered an error: {str(e)}",
                    "suggested_text": ""
                }
            ],
            "contradictions": [],
            "logs": logs
        }

def chat_about_contract(
    message: str,
    history: List[Dict[str, str]],
    contract_text: str,
    analysis_report: Dict[str, Any] = None,
    user_api_key: str = None
) -> str:
    """Answers user queries regarding the contract text, keeping a list of history."""
    llm_instance = get_llm(user_api_key)
    
    if not llm_instance:
        # Demo simulation answers
        msg_lower = message.lower()
        if "missing" in msg_lower or "clause" in msg_lower:
            if analysis_report and "missing_clauses" in analysis_report:
                clauses = [f"- {c['title']}: {c['explanation']}" for c in analysis_report["missing_clauses"]]
                if clauses:
                    return "Based on the demo analysis, the following missing clauses were detected:\n" + "\n".join(clauses)
            return "Based on the demo contract, the confidentiality clause is missing."
        if "liability" in msg_lower or "cap" in msg_lower:
            return "Based on the demo contract, Section 10 caps the vendor's liability at $5,000. This is unfavorable to the customer compared to the standard requirement, which proposes a cap representing at least 12 months of paid fees."
        if "renewal" in msg_lower or "termination" in msg_lower or "terminate" in msg_lower:
            return "Based on the demo contract, Clause 8 specifies an automatic renewal of the term. It requires a 90-day prior written notice to prevent renewal, which is flagged as a renewal trap (the industry standard is 30 days)."
        if "indemnity" in msg_lower or "indemnify" in msg_lower or "intellectual property" in msg_lower or "ip" in msg_lower:
            return "Section 5 of the contract covers IP Rights, and Section 11 states that the vendor's IP indemnification obligations are unlimited. However, this contradicts Section 10's overall $5,000 cap."
        return "This is a simulated response (Demo Mode). I can answer questions about the demo contract's liability caps ($5,000 limit), renewal terms (90-day auto-renewal notice), and IP contradictions."

    # Live Mode
    # Truncate contract text if it is too long to fit into Groq's low free-tier token limits (TPM: 6000)
    max_char_limit = 12000
    safe_contract_text = contract_text
    if len(contract_text) > max_char_limit:
        safe_contract_text = contract_text[:max_char_limit] + "\n\n... [Remaining text truncated to fit API token limits] ..."

    report_context = ""
    if analysis_report:
        contract_type = analysis_report.get("contract_type", "Unknown")
        risks = analysis_report.get("risks", [])
        missing = analysis_report.get("missing_clauses", [])
        contradictions = analysis_report.get("contradictions", [])
        
        report_context = (
            "\nHere is the summary of the analysis report generated by the review agent:\n"
            f"- Contract Type: {contract_type}\n"
            f"- Identified Risks: {json.dumps(risks, indent=2)}\n"
            f"- Missing Clauses Detected: {json.dumps(missing, indent=2)}\n"
            f"- Contradictions Detected: {json.dumps(contradictions, indent=2)}\n"
        )

    system_prompt = (
        "You are an expert legal advisor assistant reviewing a contract.\n"
        "Here is the contract text for context:\n"
        f"--- START CONTRACT TEXT ---\n{safe_contract_text}\n--- END CONTRACT TEXT ---\n"
        f"{report_context}\n"
        "Answer the user's questions about this contract objectively, highlighting critical risks or issues where applicable.\n"
        "Be extremely honest: only discuss things that are actually in the contract text or in the analysis report.\n"
        "If a clause is missing, confirm it is missing. Do not claim something exists in the contract if it is not in the text.\n"
        "Keep your response concise, professional, and clear."
    )
    
    messages = [SystemMessage(content=system_prompt)]
    
    # Add history
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
            
    # Append the new user message
    messages.append(HumanMessage(content=message))
    
    try:
        response = llm_instance.invoke(messages)
        return response.content.strip()
    except Exception as e:
        return f"Error communicating with AI: {str(e)}"