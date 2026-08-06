"""Seed the database with AI-generated questions.

Reads the cached questions produced by ``ai/question_generation.py``
(``ai/generated_questions.json``) and stores them as ``Question`` rows linked
into a single quiz. The original ``seed.py`` demo data is left untouched.

Usage:
    ../.venv/bin/python seed_ai.py              # seed from existing cache
    ../.venv/bin/python seed_ai.py --generate   # (re)generate the cache first
    ../.venv/bin/python seed_ai.py --reset      # wipe questions/quiz links first
"""

import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import delete
from sqlmodel import func, select

from app.core.database import async_session_maker, init_db
from models import (
    Answer,
    LanguageLevel,
    MediaType,
    Question,
    QuestionMedia,
    QuestionType,
    Quiz,
    QuizQuestion,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_FILE = REPO_ROOT / "ai" / "generated_questions.json"

sys.path.insert(0, str(REPO_ROOT))


async def clear_quiz_data(session) -> None:
    for model in (Answer, QuestionMedia, QuizQuestion, Question, Quiz):
        await session.exec(delete(model))
    await session.commit()


def build_config(data: dict) -> dict:
    qtype = data["type"]
    if qtype == "multiple_choice":
        return {
            "options": data["choices"],
            "correct_index": data["correct"],
            "explanations": data["explanations"],
        }
    if qtype == "multiple_selection":
        return {
            "options": data["choices"],
            "correct_indices": data["correct"],
            "explanations": data["explanations"],
        }
    if qtype == "true_false":
        return {"answer": data["correct"]}
    if qtype == "short_text":
        return {"accepted_answers": [data["correct"]]}
    raise ValueError(f"Unknown question type: {qtype!r}")


async def seed() -> None:
    await init_db()

    if "--generate" in sys.argv:
        from ai.question_generation import generate_questions, text

        questions = generate_questions(level="C1")
        CACHE_FILE.write_text(
            json.dumps([q.model_dump() for q in questions], indent=2),
            encoding="utf-8",
        )
        print(f"Generated {len(questions)} questions -> {CACHE_FILE}")
    else:
        from ai.question_generation import text

    source_text = text

    if not CACHE_FILE.exists():
        raise SystemExit(
            f"Cache not found: {CACHE_FILE}. Run `python seed_ai.py --generate` first."
        )

    payload = json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    async with async_session_maker() as session:
        if "--reset" in sys.argv:
            await clear_quiz_data(session)

        existing = (
            await session.exec(
                select(func.count(Question.id)).where(
                    Question.prompt.in_([q["prompt"] for q in payload])
                )
            )
        ).one()
        if existing > 0:
            print(
                "Database already contains these questions. Use --reset to reseed."
            )
            return

        rows = [
            Question(
                level=LanguageLevel(data["level"]),
                type=QuestionType(data["type"]),
                prompt=data["prompt"],
                suggested_score=data["suggested_score"],
                config=build_config(data),
            )
            for data in payload
        ]
        session.add_all(rows)
        await session.flush()

        for question in rows:
            session.add(
                QuestionMedia(
                    question_id=question.id,
                    type=MediaType.TEXT,
                    url=None,
                    caption=source_text,
                    position=0,
                )
            )

        quiz = Quiz(
            title="Business Etiquette (AI Generated)",
            description="C1 comprehension questions generated from the business etiquette text.",
        )
        session.add(quiz)
        await session.flush()

        for position, question in enumerate(rows):
            session.add(
                QuizQuestion(
                    quiz_id=quiz.id,
                    question_id=question.id,
                    position=position,
                )
            )

        await session.commit()
        print(
            f"Seeded: {len(rows)} questions in quiz '{quiz.title}' "
            f"(level={rows[0].level.value if rows else '-'})"
        )


if __name__ == "__main__":
    asyncio.run(seed())
