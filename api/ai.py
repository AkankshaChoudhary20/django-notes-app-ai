import json
import logging
import os

import anthropic
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
REQUEST_TIMEOUT = 20.0  # seconds - bounds how long a sync Django worker can block

MAX_NOTES_IN_CONTEXT = 200       # most recent notes considered for search/ask
MAX_CHARS_PER_NOTE = 600         # per-note truncation when building search/ask context
MAX_TOTAL_CONTEXT_CHARS = 60000  # hard stop while appending notes to a prompt

_client = None


def get_client():
    """Returns a shared Anthropic client, or None if no API key is configured."""
    global _client
    if _client is not None:
        return _client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    _client = anthropic.Anthropic(api_key=api_key).with_options(timeout=REQUEST_TIMEOUT)
    return _client


class TitleAndTags(BaseModel):
    title: str = Field(description="A concise 3-8 word title for the note")
    tags: list[str] = Field(description="1-5 short lowercase topical tags")


class AskAnswer(BaseModel):
    answer: str
    cited_note_ids: list[int]


def generate_title_and_tags(body):
    """Used on note creation, and by the manual regenerate endpoint. Never raises."""
    client = get_client()
    if not client or not body:
        return None
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=300,
            system=(
                "You generate a short title and topical tags for a personal note. "
                "Base the title and tags only on the note body provided."
            ),
            messages=[{"role": "user", "content": body[:4000]}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["title", "tags"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        text = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        return TitleAndTags(**data)
    except Exception:
        logger.exception("generate_title_and_tags failed")
        return None


def summarize_note(body):
    client = get_client()
    if not client or not body:
        return None
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=500,
            system="Summarize the user's note in 2-4 concise sentences, preserving key facts.",
            messages=[{"role": "user", "content": body[:12000]}],
        )
        return next((b.text for b in response.content if b.type == "text"), None)
    except Exception:
        logger.exception("summarize_note failed")
        return None


def improve_writing(body):
    """Returns a suggested rewrite. Caller must never auto-save this."""
    client = get_client()
    if not client or not body:
        return None
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=1500,
            system=(
                "You are an editor. Rewrite the note for clarity and grammar while "
                "preserving the author's meaning, tone, and formatting. "
                "Return only the rewritten note text, nothing else."
            ),
            messages=[{"role": "user", "content": body[:12000]}],
        )
        return next((b.text for b in response.content if b.type == "text"), None)
    except Exception:
        logger.exception("improve_writing failed")
        return None


def _build_note_context(notes):
    """notes: iterable of Note model instances, most-recent-first."""
    context, total = [], 0
    for note in list(notes)[:MAX_NOTES_IN_CONTEXT]:
        excerpt = (note.body or "")[:MAX_CHARS_PER_NOTE]
        total += len(excerpt)
        if total > MAX_TOTAL_CONTEXT_CHARS:
            break
        context.append({"id": note.id, "title": note.title or "", "excerpt": excerpt})
    return context


def search_notes(query, notes):
    client = get_client()
    if not client or not query:
        return None
    context = _build_note_context(notes)
    if not context:
        return []
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=400,
            system=(
                "Given a search query and a list of the user's notes (id, title, excerpt), "
                "return the ids of notes relevant to the query, most relevant first. "
                "Return an empty list if nothing is relevant."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nNotes: {json.dumps(context)}",
                }
            ],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "note_ids": {"type": "array", "items": {"type": "integer"}}
                        },
                        "required": ["note_ids"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        text = next(b.text for b in response.content if b.type == "text")
        candidate_ids = json.loads(text)["note_ids"]
        valid_ids = {n["id"] for n in context}
        return [i for i in candidate_ids if i in valid_ids]  # drop hallucinated ids
    except Exception:
        logger.exception("search_notes failed")
        return None


def ask_notes(question, notes):
    client = get_client()
    if not client or not question:
        return None
    context = _build_note_context(notes)
    try:
        response = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=800,
            system=(
                "Answer the user's question using ONLY the information in the provided notes. "
                "If the notes don't contain the answer, say so plainly. "
                "cited_note_ids must only contain ids of notes you actually used."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nNotes: {json.dumps(context)}",
                }
            ],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string"},
                            "cited_note_ids": {"type": "array", "items": {"type": "integer"}},
                        },
                        "required": ["answer", "cited_note_ids"],
                        "additionalProperties": False,
                    },
                }
            },
        )
        text = next(b.text for b in response.content if b.type == "text")
        data = json.loads(text)
        valid_ids = {n["id"] for n in context}
        data["cited_note_ids"] = [i for i in data["cited_note_ids"] if i in valid_ids]
        return AskAnswer(**data)
    except Exception:
        logger.exception("ask_notes failed")
        return None
