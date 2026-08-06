"""Typed HTTP client for the Quiz backend API.

Methods return pydantic models (parsed from the JSON responses) instead of
raw dicts, so the rest of the app never touches dictionaries.
"""

from __future__ import annotations

import httpx

from models.answer import AnswerRead
from models.attempt import Attempt, AttemptResult
from models.quiz import Quiz
from models.question import Question
from models.attempt import Token, User
from config import API_TIMEOUT, API_URL
from services.exceptions import QuizApiError


class QuizApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = API_TIMEOUT):
        self.base_url = (base_url or API_URL).rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    @staticmethod
    def _headers(token: str | None = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def _handle(resp: httpx.Response):
        if resp.status_code >= 400:
            detail = resp.text
            try:
                detail = resp.json().get("detail", detail)
            except Exception:
                pass
            raise QuizApiError(resp.status_code, detail)
        if resp.status_code == 204:
            return None
        return resp.json()

    # ---------- auth ----------

    def login(self, email: str, password: str = "") -> Token:
        # The dev token endpoint ignores the password but requires a non-empty
        # form field, so fall back to a placeholder when none is given.
        password = password if password else "stone-quiz"
        resp = self._client.post(
            f"{self.base_url}/api/v1/auth/token",
            data={"username": email, "password": password},
        )
        return Token.model_validate(self._handle(resp))

    def me(self, token: str) -> User:
        resp = self._client.get(
            f"{self.base_url}/api/v1/users/me", headers=self._headers(token)
        )
        return User.model_validate(self._handle(resp))

    # ---------- quizzes / questions ----------

    def list_quizzes(self, token: str) -> list[Quiz]:
        resp = self._client.get(
            f"{self.base_url}/api/v1/quizzes", headers=self._headers(token)
        )
        return [Quiz.model_validate(item) for item in self._handle(resp)]

    def get_question(self, token: str, question_id: str) -> Question:
        resp = self._client.get(
            f"{self.base_url}/api/v1/questions/{question_id}",
            headers=self._headers(token),
        )
        return Question.model_validate(self._handle(resp))

    # ---------- attempts ----------

    def start_attempt(self, token: str, quiz_id: str) -> Attempt:
        resp = self._client.post(
            f"{self.base_url}/api/v1/attempts",
            headers=self._headers(token),
            json={"quiz_id": quiz_id},
        )
        return Attempt.model_validate(self._handle(resp))

    def submit_answer(
        self, token: str, attempt_id: str, question_id: str, response: dict
    ) -> AnswerRead:
        resp = self._client.post(
            f"{self.base_url}/api/v1/attempts/{attempt_id}/answers",
            headers=self._headers(token),
            json={"question_id": question_id, "response": response},
        )
        return AnswerRead.model_validate(self._handle(resp))

    def finish_attempt(self, token: str, attempt_id: str) -> AttemptResult:
        resp = self._client.post(
            f"{self.base_url}/api/v1/attempts/{attempt_id}/finish",
            headers=self._headers(token),
        )
        return AttemptResult.model_validate(self._handle(resp))