from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class MeetingNote(Base):
    __tablename__ = "meeting_notes"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    topic: Mapped[str] = mapped_column(String(80), index=True, default="general")
    attendees: Mapped[str] = mapped_column(String(240), default="")
    body: Mapped[str] = mapped_column(Text)
    meeting_date: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class NoteChunk(Base):
    __tablename__ = "note_chunks"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    note_id: Mapped[str] = mapped_column(String(32), index=True)
    topic: Mapped[str] = mapped_column(String(80), index=True)
    text: Mapped[str] = mapped_column(Text)
