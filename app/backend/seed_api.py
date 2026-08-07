"""Seed a running backend through its HTTP API.

Reads ``app/ai/generated_questions.json`` and creates the questions, a C1
reading quiz, and their links via the public API of a target deployment.
No direct database access is required.

Usage:
    .venv/bin/python seed_api.py --base-url https://quiz-backend-wfwo.onrender.com
    .venv/bin/python seed_api.py --base-url http://localhost:8000 --email seed@example.com
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app import models  # noqa: F401  (registers tables in SQLModel.metadata)

API_PREFIX = "/api/v1"

DEFAULT_BASE_URL = (
    os.environ.get("API_BASE_URL")
    or os.environ.get("QUIZ_API_URL")
    or "https://quiz-backend-wfwo.onrender.com"
)
DEFAULT_EMAIL = "seed@example.com"

# DEFAULT_JSON = Path(__file__).resolve().parents[2] / "app" / "ai" / "generated_questions.json"
# QUIZ_TITLE = "Cross-Cultural Communication"
# QUIZ_DESCRIPTION = "C1 reading comprehension on cross-cultural business communication"
# QUIZ_CATEGORY = "reading"
# QUIZ_LEVEL = "C1"
# SOURCE_MEDIA_URL = "https://storage.googleapis.com/quiz_public_bucket/cross_cultural_communication.md"
# SOURCE_MEDIA_CAPTION = "Reading passage"
# SOURCE_MEDIA_TYPE = "text"

DEFAULT_JSON = Path(__file__).resolve().parents[2] / "app" / "ai" / "generated_questions_listening.json"
QUIZ_TITLE = "Birthday Parties"
QUIZ_DESCRIPTION = "C1 listening comprehension on Birthday parties"
QUIZ_CATEGORY = "listening"
QUIZ_LEVEL = "C1"
SOURCE_MEDIA_URL = "https://storage.googleapis.com/quiz_public_bucket/fixed.mp3"
SOURCE_MEDIA_CAPTION = "Listen carefully to the audio"
SOURCE_MEDIA_TYPE = "audio"


def _config_for(item: dict) -> dict:
    qtype = item["type"]
    if qtype == "multiple_choice":
        return {"options": item["choices"], "correct_index": item["correct"]}
    if qtype == "multiple_selection":
        return {"options": item["choices"], "correct_indices": item["correct"]}
    if qtype == "true_false":
        return {"answer": bool(item["correct"])}
    if qtype == "short_text":
        return {"accepted_answers": [str(item["correct"])]}
    raise ValueError(f"Unsupported question type: {qtype!r}")


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        detail = resp.text
        try:
            detail = resp.json().get("detail", detail)
        except Exception:
            pass
        raise RuntimeError(f"{resp.status_code}: {detail}")


def _normalize_db_url(url: str) -> str:
    """Ensure SQLAlchemy async engines get an async driver for Postgres."""
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        scheme = url.split("://", 1)[0]
        if "+" not in scheme:
            return "postgresql+asyncpg://" + url.split("://", 1)[1]
    return url


async def _wipe_database(database_url: str) -> None:
    """Drop and recreate all tables, wiping the database via direct DB access."""
    engine = create_async_engine(_normalize_db_url(database_url))
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
    finally:
        await engine.dispose()
    print(f"Database wiped: all tables dropped and recreated ({database_url}).")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed a backend via its HTTP API")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--json", dest="json_path", default=str(DEFAULT_JSON), type=Path)
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL")
        or "postgresql+asyncpg://postgres:postgres@localhost:5432/quiz",
        help="Async DB URL used by --reset (defaults to a local Postgres URL or "
        "the DATABASE_URL env var).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="wipe the database directly (drop & recreate all tables) before seeding",
    )
    args = parser.parse_args()

    if args.reset:
        asyncio.run(_wipe_database(args.database_url))

    base = args.base_url.rstrip("/")
    questions_path = Path(args.json_path).expanduser().resolve()
    if not questions_path.exists():
        print(f"questions file not found: {questions_path}", file=sys.stderr)
        return 1

    items = json.loads(questions_path.read_text(encoding="utf-8"))

    with httpx.Client(base_url=base, timeout=60) as client:
        # 1. Auth (the token route auto-creates the user).
        resp = client.post(
            f"{API_PREFIX}/auth/token",
            data={"username": args.email, "password": "x"},
        )
        _raise_for_status(resp)
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Authenticated as {args.email}")

        # 2. Existing data, for idempotency.
        questions_resp = client.get(f"{API_PREFIX}/questions")
        _raise_for_status(questions_resp)
        existing_by_prompt = {
            q["prompt"]: q["id"] for q in (questions_resp.json() if questions_resp.content else [])
        }
        quizzes_resp = client.get(f"{API_PREFIX}/quizzes")
        _raise_for_status(quizzes_resp)
        existing_quizzes = {
            q["title"]: q for q in (quizzes_resp.json() if quizzes_resp.content else [])
        }

        # 3. Create questions (reusing any with an identical prompt).
        question_ids: list[str] = []
        created = reused = 0
        for item in items:
            prompt = item["prompt"]
            existing_id = existing_by_prompt.get(prompt)
            if existing_id is not None:
                question_ids.append(existing_id)
                reused += 1
                continue
            payload = {
                "type": item["type"],
                "prompt": prompt,
                "suggested_score": float(item.get("suggested_score", 1.0)),
                "config": _config_for(item),
            }
            resp = client.post(f"{API_PREFIX}/questions", json=payload, headers=headers)
            _raise_for_status(resp)
            question_ids.append(resp.json()["id"])
            created += 1

        # 4. Create the quiz (reusing one with the same title).
        quiz = existing_quizzes.get(QUIZ_TITLE)
        if quiz is None:
            resp = client.post(
                f"{API_PREFIX}/quizzes",
                json={
                    "title": QUIZ_TITLE,
                    "description": QUIZ_DESCRIPTION,
                    "category": QUIZ_CATEGORY,
                    "level": QUIZ_LEVEL,
                },
                headers=headers,
            )
            _raise_for_status(resp)
            quiz = resp.json()
            print(f"Created quiz {quiz['id']} ({QUIZ_TITLE})")
        else:
            print(f"Reused existing quiz {quiz['id']} ({QUIZ_TITLE})")

        # 5. Link questions to the quiz in order.
        quiz_id = quiz["id"]
        already_linked = set(quiz.get("question_ids") or [])
        linked = skipped = 0
        for position, qid in enumerate(question_ids):
            if qid in already_linked:
                skipped += 1
                continue
            resp = client.post(
                f"{API_PREFIX}/quizzes/{quiz_id}/questions",
                json={"question_id": qid, "position": position},
                headers=headers,
            )
            _raise_for_status(resp)
            linked += 1

        # 6. Attach the shared source document as TEXT media to each question.
        media_created = media_reused = 0
        for qid in question_ids:
            resp = client.get(f"{API_PREFIX}/media", params={"question_id": qid})
            _raise_for_status(resp)
            existing = resp.json() if resp.content else []
            if any(
                m.get("type") == SOURCE_MEDIA_TYPE and m.get("url") == SOURCE_MEDIA_URL
                for m in existing
            ):
                media_reused += 1
                continue
            resp = client.post(
                f"{API_PREFIX}/media",
                json={
                    "question_id": qid,
                    "type": SOURCE_MEDIA_TYPE,
                    "url": SOURCE_MEDIA_URL,
                    "caption": SOURCE_MEDIA_CAPTION,
                    "position": 0,
                },
                headers=headers,
            )
            _raise_for_status(resp)
            media_created += 1

        print(
            f"Done: {created} questions created, {reused} reused; "
            f"{linked} linked, {skipped} already linked; "
            f"{media_created} media created, {media_reused} already present."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
