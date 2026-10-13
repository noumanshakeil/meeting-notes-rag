from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import MeetingNote, NoteChunk
from backend.services.rag_core import Hit, chunk_text, pack_citations, score_chunk

async def ingest(
    session: AsyncSession,
    title: str,
    body: str,
    topic: str = "general",
    attendees: str = "",
    meeting_date: str = "",
) -> dict:
    note = MeetingNote(
        id=uuid.uuid4().hex[:10],
        title=title.strip()[:200],
        topic=(topic or "general").lower()[:80],
        attendees=attendees.strip()[:240],
        body=body.strip(),
        meeting_date=meeting_date.strip()[:32],
    )
    session.add(note)
    await session.flush()
    n = 0
    for piece in chunk_text(body, size=360, overlap=50):
        session.add(
            NoteChunk(
                id=uuid.uuid4().hex[:12],
                note_id=note.id,
                topic=note.topic,
                text=piece,
            )
        )
        n += 1
    await session.commit()
    return {"note_id": note.id, "chunks": n}

async def list_notes(session: AsyncSession, topic: str | None = None) -> list[MeetingNote]:
    stmt = select(MeetingNote)
    if topic:
        stmt = stmt.where(MeetingNote.topic == topic.lower())
    return list((await session.execute(stmt.order_by(MeetingNote.created_at.desc()))).scalars())

async def ask(session: AsyncSession, question: str, topic: str | None = None) -> dict:
    stmt = select(NoteChunk)
    if topic:
        stmt = stmt.where(NoteChunk.topic == topic.lower())
    chunks = list((await session.execute(stmt)).scalars())
    notes = {n.id: n for n in (await session.execute(select(MeetingNote))).scalars()}
    hits: list[Hit] = []
    for ch in chunks:
        s = score_chunk(question, ch.text)
        if s <= 0:
            continue
        note = notes.get(ch.note_id)
        title = note.title if note else ch.note_id
        hits.append(
            Hit(
                chunk_id=ch.id,
                document_id=ch.note_id,
                title=f"{title} [{ch.topic}]",
                text=ch.text,
                score=s,
                meta={
                    "topic": ch.topic,
                    "attendees": getattr(note, "attendees", ""),
                    "meeting_date": getattr(note, "meeting_date", ""),
                },
            )
        )
    hits.sort(key=lambda h: h.score, reverse=True)
    hits = hits[:6]
    context = pack_citations(hits) if hits else "(no notes indexed)"
    llm = get_llm()
    answer = await llm.complete(
        f"Meeting notes assistant. Cite snippets. Q: {question}\n\nNOTES:\n{context}",
        system="Summarize decisions and action items; do not invent attendees.",
    )
    return {
        "answer": answer,
        "citations": [
            {
                "index": i,
                "note_id": h.document_id,
                "title": h.title,
                "topic": h.meta.get("topic"),
                "score": round(h.score, 3),
                "snippet": h.text[:220],
            }
            for i, h in enumerate(hits, start=1)
        ],
    }
