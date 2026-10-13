from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import notes as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, topic: str | None = None, db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Meeting Notes RAG",
            "topic": topic or "",
            "notes": await svc.list_notes(db, topic or None),
            "answer": None,
            "citations": [],
        },
    )

@router.post("/ui/notes")
async def ui_add(
    title: str = Form(...),
    body: str = Form(...),
    topic: str = Form("general"),
    attendees: str = Form(""),
    meeting_date: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    await svc.ingest(db, title, body, topic, attendees, meeting_date)
    return RedirectResponse(f"/?topic={topic}", status_code=303)

@router.post("/ui/ask", response_class=HTMLResponse)
async def ui_ask(
    request: Request,
    question: str = Form(...),
    topic: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.ask(db, question, topic or None)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Meeting Notes RAG",
            "topic": topic,
            "notes": await svc.list_notes(db, topic or None),
            "answer": result["answer"],
            "citations": result["citations"],
            "question": question,
        },
    )
