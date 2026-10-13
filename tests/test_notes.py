import pytest

@pytest.mark.asyncio
async def test_ingest_ask(client):
    r = await client.post(
        "/api/notes",
        json={
            "title": "Eng standup",
            "topic": "standup",
            "attendees": "ada,grace",
            "meeting_date": "2026-10-13",
            "body": "We decided to ship the RAG upgrade behind a feature flag. "
            "Ada owns the CI flake. Grace will review the docs PR tomorrow.",
        },
    )
    assert r.status_code == 200
    ask = await client.post(
        "/api/ask", json={"question": "Who owns the CI flake?", "topic": "standup"}
    )
    assert ask.status_code == 200
    assert ask.json()["citations"]
