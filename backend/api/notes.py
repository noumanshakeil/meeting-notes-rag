from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import notes as svc

class NoteIn(BaseModel):
    title: str = Field(min_length=2)
    body: str = Field(min_length=20)
    topic: str = "general"
    attendees: str = ""
    meeting_date: str = ""

class AskIn(BaseModel):
    question: str = Field(min_length=3)
    topic: str | None = None

router = APIRouter()

@router.get("/notes")
async def list_notes(topic: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_notes(db, topic)
    return {
        "notes": [
            {
                "id": n.id,
                "title": n.title,
                "topic": n.topic,
                "attendees": n.attendees,
                "meeting_date": n.meeting_date,
            }
            for n in rows
        ]
    }

@router.post("/notes")
async def create(payload: NoteIn, db: AsyncSession = Depends(get_db)):
    return await svc.ingest(
        db, payload.title, payload.body, payload.topic, payload.attendees, payload.meeting_date
    )

@router.post("/ask")
async def ask(payload: AskIn, db: AsyncSession = Depends(get_db)):
    return await svc.ask(db, payload.question, payload.topic)
