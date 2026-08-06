from datetime import datetime, UTC
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

# -------------------------
# Enums
# -------------------------

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_SELECTION = "multiple_selection"
    TRUE_FALSE = "true_false"
    SHORT_TEXT = "short_text"


class MediaType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class LanguageLevel(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class QuizCategory(str, Enum):
    READING = "reading"
    LISTENING = "listening"
    VOCABULARY = "vocabulary"

# -------------------------
# Users
# -------------------------

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    level: LanguageLevel

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
        ),
    )

    attempts: list["QuizAttempt"] = Relationship(back_populates="user")

# -------------------------
# Quiz -> Question mapping
# -------------------------

class QuizQuestion(SQLModel, table=True):
    __tablename__ = "quiz_questions"

    quiz_id: UUID = Field(
        foreign_key="quizzes.id",
        primary_key=True,
    )

    question_id: UUID = Field(
        foreign_key="questions.id",
        primary_key=True,
    )

    position: int = 0

# -------------------------
# Quiz
# -------------------------

class Quiz(SQLModel, table=True):
    __tablename__ = "quizzes"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str
    description: str | None = None

    category: QuizCategory = QuizCategory.READING
    level: LanguageLevel = LanguageLevel.A1

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    questions: list["Question"] = Relationship(
        back_populates="quizzes",
        link_model=QuizQuestion,
    )

    attempts: list["QuizAttempt"] = Relationship(back_populates="quiz")


# -------------------------
# Question
# -------------------------

class Question(SQLModel, table=True):
    __tablename__ = "questions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    type: QuestionType

    prompt: str

    suggested_score: float = 1.0

    config: dict = Field(sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    media: list["QuestionMedia"] = Relationship(back_populates="question")

    quizzes: list["Quiz"] = Relationship(
        back_populates="questions",
        link_model=QuizQuestion,
    )

    answers: list["Answer"] = Relationship(back_populates="question")

# -------------------------
# Media
# -------------------------

class QuestionMedia(SQLModel, table=True):
    __tablename__ = "question_media"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    question_id: UUID = Field(
        foreign_key="questions.id",
        index=True,
    )

    type: MediaType
    url: str | None = None
    caption: str | None = None
    position: int = 0

    question: Question = Relationship(back_populates="media")

# -------------------------
# Quiz Attempt
# -------------------------

class QuizAttempt(SQLModel, table=True):
    __tablename__ = "quiz_attempts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    quiz_id: UUID = Field(
        foreign_key="quizzes.id",
        index=True,
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
    )

    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None

    score: float | None = None

    user: User = Relationship(back_populates="attempts")

    quiz: "Quiz" = Relationship(back_populates="attempts")

    answers: list["Answer"] = Relationship(
        back_populates="attempt",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
    })


# -------------------------
# Answers
# -------------------------

class Answer(SQLModel, table=True):
    __tablename__ = "answers"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_answer_per_question",
        ),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    attempt_id: UUID = Field(
        foreign_key="quiz_attempts.id",
        index=True,
    )

    question_id: UUID = Field(
        foreign_key="questions.id",
        index=True,
    )

    response: dict = Field(sa_column=Column(JSON))

    is_correct: bool | None = None

    points_awarded: float = 0

    answered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    question: Question = Relationship(back_populates="answers")

    attempt: QuizAttempt = Relationship(back_populates="answers")
