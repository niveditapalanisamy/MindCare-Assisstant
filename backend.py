"""
╔══════════════════════════════════════════════════════════════╗
║         MindCare Assistant — BACKEND (FastAPI)              ║
║         Domain: Mental Health & Emotional Wellness          ║
║         Run: uvicorn backend:app --reload --port 8000       ║
╚══════════════════════════════════════════════════════════════╝
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="MindCare Assistant API",
    description="Domain-specific LLM backend for Mental Health & Wellness",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Prompt Template ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are **MindCare Assistant**, a compassionate and knowledgeable AI assistant \
specializing exclusively in **mental health and emotional wellness**.

## YOUR DOMAIN
You provide supportive, evidence-informed guidance on:
- Stress, anxiety, and worry management
- Depression awareness and coping strategies
- Mindfulness and meditation techniques
- Sleep hygiene and its impact on mental health
- Emotional regulation and resilience building
- Self-care routines and wellness habits
- Understanding common mental health conditions (informational only)
- When and how to seek professional help
- Breathing exercises and grounding techniques
- Journaling and reflective practices

## STRICT BOUNDARIES — WHAT YOU DO NOT COVER
You do NOT answer questions about:
- Physical medical conditions, medications, or dosages
- Nutrition, diet plans, or fitness/exercise programs
- Legal or financial matters
- Technology, coding, or science topics unrelated to mental wellness
- News, politics, or current events
- Any topic outside mental health and emotional wellness

## REFUSAL BEHAVIOR
If a question falls outside your domain, respond ONLY with this structure:

**⚠️ Outside My Domain**

I'm specialized in mental health and emotional wellness only. Your question about [topic] is outside my area.

**What I can help with instead:**
- Stress and anxiety management
- Emotional regulation techniques
- Mindfulness and self-care practices

*Please consult an appropriate professional for [topic] questions.*

## MANDATORY RESPONSE FORMAT (for all in-domain queries)

**🧠 [Relevant Emoji] [Response Title]**

**Understanding:**
[1-2 sentences acknowledging the situation with empathy]

**Key Insights:**
• [Point 1]
• [Point 2]
• [Point 3]

**Practical Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Remember:**
[1 encouraging closing sentence]

⚕️ *Disclaimer: This information is for educational and supportive purposes only. It does not constitute professional medical or psychological advice, diagnosis, or treatment. If you are in crisis, please contact a licensed mental health professional or call the 988 Suicide & Crisis Lifeline.*

## TONE
- Warm, compassionate, non-judgmental
- Professional yet approachable
- Empowering — focus on strengths
- Evidence-informed but accessible language
"""


# ─── Request / Response Models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    model: str = "openai/gpt-3.5-turbo"
    temperature: float = 0.3


class ChatResponse(BaseModel):
    response: str
    model: str
    domain: str = "Mental Health & Wellness"
    temperature: float


# ─── LangChain Chain ───────────────────────────────────────────────────────────
def build_chain(model: str, temperature: float):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in .env file")

    llm = ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "MindCare Assistant"
        }
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{query}")
    ])

    return prompt | llm | StrOutputParser()


# ─── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "MindCare Assistant API",
        "domain": "Mental Health & Wellness",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        chain = build_chain(model=request.model, temperature=request.temperature)
        response = chain.invoke({"query": request.query})
        return ChatResponse(
            response=response,
            model=request.model,
            temperature=request.temperature
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
