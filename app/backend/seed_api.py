"""Seed a running backend through its HTTP API.

Reads ``app/ai/questions_cache.json`` and creates the questions, a C1
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

DEFAULT_JSON = Path(__file__).resolve().parents[2] / "app" / "ai" / "questions_cache.json"
# Quiz title/description/category/level and the shared media (type/url/
# caption) all come from the JSON's "quiz" key now (see
# ai/question_generation.py) instead of being hardcoded here. Point --json at
# questions_cache.json to seed the listening quiz instead.


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

    payload = json.loads(questions_path.read_text(encoding="utf-8"))
    quiz_data = payload["quiz"]
    items = payload["questions"]

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
        quiz_title = quiz_data["title"]
        quiz = existing_quizzes.get(quiz_title)
        if quiz is None:
            resp = client.post(
                f"{API_PREFIX}/quizzes",
                json={
                    "title": quiz_title,
                    "description": quiz_data["description"],
                    "category": quiz_data["category"],
                    "level": quiz_data["level"],
                },
                headers=headers,
            )
            _raise_for_status(resp)
            quiz = resp.json()
            print(f"Created quiz {quiz['id']} ({quiz_title})")
        else:
            print(f"Reused existing quiz {quiz['id']} ({quiz_title})")

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

        # 6. Attach the shared source document as media on the quiz itself
        #    (shared context for every question, not duplicated per question).
        media_type = quiz_data["media_type"]
        media_url = quiz_data["media_url"]
        media_caption = quiz_data["media_caption"]
        media_resp = client.get(f"{API_PREFIX}/quiz-media", params={"quiz_id": quiz_id})
        _raise_for_status(media_resp)
        existing_media = media_resp.json() if media_resp.content else []
        media_reused = any(
            m.get("type") == media_type and m.get("url") == media_url
            for m in existing_media
        )
        if not media_reused:
            resp = client.post(
                f"{API_PREFIX}/quiz-media",
                json={
                    "quiz_id": quiz_id,
                    "type": media_type,
                    "url": media_url,
                    "caption": media_caption,
                    "position": 0,
                },
                headers=headers,
            )
            _raise_for_status(resp)

        print(
            f"Done: {created} questions created, {reused} reused; "
            f"{linked} linked, {skipped} already linked; "
            f"quiz media {'already present' if media_reused else 'created'}."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
