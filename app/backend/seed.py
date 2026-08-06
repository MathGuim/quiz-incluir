"""Seed the database with demo data.

Usage:
    .venv/bin/python seed.py              # seed if tables empty
    .venv/bin/python seed.py --reset      # wipe and reseed
"""

import asyncio
import sys
from datetime import datetime, timedelta, UTC

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
    QuizAttempt,
    QuizQuestion,
    User,
)


async def clear_all(session) -> None:
    for model in (Answer, QuizAttempt, QuizQuestion, QuestionMedia, Question, Quiz, User):
        await session.exec(delete(model))
    await session.commit()


async def has_data(session) -> bool:
    count = (await session.exec(select(func.count(User.id)))).one()
    return count > 0


async def seed() -> None:
    await init_db()
    async with async_session_maker() as session:
        if "--reset" in sys.argv:
            await clear_all(session)

        if await has_data(session):
            print("Database already has data. Use --reset to wipe and reseed.")
            return

        users = [
            User(email="anna@example.com", level=LanguageLevel.A1),
            User(email="ben@example.com", level=LanguageLevel.A1),
            User(email="carla@example.com", level=LanguageLevel.B1),
            User(email="diego@example.com", level=LanguageLevel.C1),
        ]
        session.add_all(users)

        questions = [
            Question(
                level=LanguageLevel.A1,
                type=QuestionType.MULTIPLE_CHOICE,
                prompt="Which word is a fruit?",
                suggested_score=1.0,
                config={"options": ["apple", "table", "chair", "book"], "correct_index": 0},
            ),
            Question(
                level=LanguageLevel.A1,
                type=QuestionType.MULTIPLE_CHOICE,
                prompt="What is the opposite of 'hot'?",
                suggested_score=1.0,
                config={"options": ["cold", "warm", "boiling", "sunny"], "correct_index": 0},
            ),
            Question(
                level=LanguageLevel.A1,
                type=QuestionType.TRUE_FALSE,
                prompt="The sun rises in the east.",
                suggested_score=1.0,
                config={"answer": True},
            ),
            Question(
                level=LanguageLevel.A1,
                type=QuestionType.SHORT_TEXT,
                prompt="Complete the sentence: I ____ a student.",
                suggested_score=1.0,
                config={"accepted_answers": ["am"]},
            ),
            Question(
                level=LanguageLevel.A2,
                type=QuestionType.MULTIPLE_SELECTION,
                prompt="Which of these are animals?",
                suggested_score=1.0,
                config={
                    "options": ["dog", "rose", "cat", "hammer"],
                    "correct_indices": [0, 2],
                },
            ),
            Question(
                level=LanguageLevel.A2,
                type=QuestionType.MULTIPLE_CHOICE,
                prompt="Choose the correct past tense: 'I ____ to school yesterday.'",
                suggested_score=1.0,
                config={"options": ["go", "went", "gone", "going"], "correct_index": 1},
            ),
            Question(
                level=LanguageLevel.B1,
                type=QuestionType.TRUE_FALSE,
                prompt="'Their' and 'they're' mean the same thing.",
                suggested_score=1.0,
                config={"answer": False},
            ),
            Question(
                level=LanguageLevel.B1,
                type=QuestionType.MULTIPLE_CHOICE,
                prompt="Which word is a synonym of 'happy'?",
                suggested_score=1.0,
                config={"options": ["sad", "angry", "joyful", "tired"], "correct_index": 2},
            ),
            Question(
                level=LanguageLevel.B2,
                type=QuestionType.SHORT_TEXT,
                prompt="Give the correct comparative form of 'good'.",
                suggested_score=1.0,
                config={"accepted_answers": ["better"]},
            ),
            Question(
                level=LanguageLevel.C1,
                type=QuestionType.MULTIPLE_SELECTION,
                prompt="Which sentences are grammatically correct?",
                suggested_score=1.0,
                config={
                    "options": [
                        "She has been working all day.",
                        "He don't like coffee.",
                        "They have lived here for years.",
                        "Me go to the store.",
                    ],
                    "correct_indices": [0, 2],
                },
            ),
            Question(
                level=LanguageLevel.C1,
                type=QuestionType.MULTIPLE_CHOICE,
                prompt="Select the most formal way to request assistance.",
                suggested_score=1.0,
                config={
                    "options": [
                        "I would be grateful if you could help me.",
                        "Help me now.",
                        "Gimme a hand.",
                        "You need to help me.",
                    ],
                    "correct_index": 0,
                },
            ),
            Question(
                level=LanguageLevel.C2,
                type=QuestionType.MULTIPLE_CHOICE,
                prompt="Choose the word that best fits: 'His ______ disregard for rules alarmed his colleagues.'",
                suggested_score=1.0,
                config={
                    "options": ["flagrant", "lukewarm", "paltry", "bashful"],
                    "correct_index": 0,
                },
            ),
        ]
        session.add_all(questions)

        media = [
            QuestionMedia(
                question_id=questions[0].id,
                type=MediaType.IMAGE,
                url="https://storage.googleapis.com/quiz_public_bucket/sunrise.jpg",
                caption="Fruits on a table",
                position=0,
            ),
            QuestionMedia(
                question_id=questions[2].id,
                type=MediaType.IMAGE,
                url="https://storage.googleapis.com/quiz_public_bucket/sunrise.jpg",
                caption="Sunrise over the ocean",
                position=0,
            ),
            QuestionMedia(
                question_id=questions[5].id,
                type=MediaType.AUDIO,
                url="https://storage.googleapis.com/quiz_public_bucket/en-planning-a-vacation-69.mp3",
                caption="Listen to the sentence",
                position=0,
            ),
            QuestionMedia(
                question_id=questions[1].id,
                type=MediaType.VIDEO,
                url="https://www.youtube.com/watch?v=lJ7dWD_9SEw",
                caption="Listen to the video",
                position=0,
            ),
        ]
        session.add_all(media)

        quizzes = [
            Quiz(title="Beginner Basics", description="A1 level essentials"),
            Quiz(title="Intermediate Check", description="B1 grammar and vocabulary"),
            Quiz(title="Advanced Mastery", description="C1-C2 challenge"),
        ]
        session.add_all(quizzes)

        link_spec = [
            (quizzes[0], [0, 1, 2, 3]),
            (quizzes[1], [4, 5, 6, 7]),
            (quizzes[2], [8, 9, 10, 11]),
        ]
        for quiz, indices in link_spec:
            for position, index in enumerate(indices):
                session.add(
                    QuizQuestion(
                        quiz_id=quiz.id,
                        question_id=questions[index].id,
                        position=position,
                    )
                )

        attempts = [
            QuizAttempt(
                quiz_id=quizzes[0].id,
                user_id=users[0].id,
                started_at=datetime.now(UTC) - timedelta(days=2),
                finished_at=datetime.now(UTC) - timedelta(days=2),
                score=2.0,
            ),
            QuizAttempt(
                quiz_id=quizzes[0].id,
                user_id=users[1].id,
                started_at=datetime.now(UTC) - timedelta(days=1),
                finished_at=None,
                score=None,
            ),
            QuizAttempt(
                quiz_id=quizzes[1].id,
                user_id=users[2].id,
                started_at=datetime.now(UTC) - timedelta(hours=3),
                finished_at=datetime.now(UTC) - timedelta(hours=3),
                score=3.0,
            ),
            QuizAttempt(
                quiz_id=quizzes[2].id,
                user_id=users[3].id,
                started_at=datetime.now(UTC) - timedelta(hours=1),
                finished_at=None,
                score=None,
            ),
        ]
        session.add_all(attempts)

        answers = [
            Answer(
                attempt_id=attempts[0].id,
                question_id=questions[0].id,
                response={"selected": "apple"},
                is_correct=True,
                points_awarded=1.0,
                answered_at=datetime.now(UTC) - timedelta(days=2),
            ),
            Answer(
                attempt_id=attempts[0].id,
                question_id=questions[1].id,
                response={"selected": "cold"},
                is_correct=True,
                points_awarded=1.0,
                answered_at=datetime.now(UTC) - timedelta(days=2),
            ),
            Answer(
                attempt_id=attempts[0].id,
                question_id=questions[2].id,
                response={"selected": True},
                is_correct=True,
                points_awarded=1.0,
                answered_at=datetime.now(UTC) - timedelta(days=2),
            ),
            Answer(
                attempt_id=attempts[0].id,
                question_id=questions[3].id,
                response={"text": "is"},
                is_correct=False,
                points_awarded=0.0,
                answered_at=datetime.now(UTC) - timedelta(days=2),
            ),
            Answer(
                attempt_id=attempts[2].id,
                question_id=questions[4].id,
                response={"selected": ["dog", "cat"]},
                is_correct=True,
                points_awarded=1.0,
                answered_at=datetime.now(UTC) - timedelta(hours=3),
            ),
            Answer(
                attempt_id=attempts[2].id,
                question_id=questions[5].id,
                response={"selected": "go"},
                is_correct=False,
                points_awarded=0.0,
                answered_at=datetime.now(UTC) - timedelta(hours=3),
            ),
        ]
        session.add_all(answers)

        await session.commit()
        print(
            f"Seeded: {len(users)} users, {len(questions)} questions, "
            f"{len(media)} media, {len(quizzes)} quizzes, "
            f"{len(attempts)} attempts, {len(answers)} answers"
        )


if __name__ == "__main__":
    asyncio.run(seed())
