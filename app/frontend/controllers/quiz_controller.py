"""Quiz workflow: load quizzes, run an attempt, finish it.

Controllers mutate :class:`AppState` and call the API; they never build UI.
Screens re-render automatically because they subscribe to the observable state.
"""

from __future__ import annotations

from models.attempt import AttemptResult
from models.quiz import Quiz
from services.api import QuizApiClient
from state.app_state import AppState


class QuizController:
    def __init__(self, state: AppState, api: QuizApiClient):
        self.state = state
        self.api = api

    # ---------- loading ----------

    async def list_quizzes(self) -> list[Quiz]:
        return await self.api.list_quizzes(self.state.token)

    async def start(self, quiz: Quiz) -> None:
        questions = [
            await self.api.get_question(self.state.token, str(qid))
            for qid in quiz.question_ids
        ]
        attempt = await self.api.start_attempt(self.state.token, str(quiz.id))
        if not questions:
            raise ValueError("This quiz has no questions.")
        self.state.quiz = quiz
        self.state.questions = questions
        self.state.answers = {}
        self.state.attempt_id = str(attempt.id)
        self.state.current_index = 0
        self.state.finished = False
        self.state.result = None

    # ---------- navigation within the attempt ----------

    @property
    def total(self) -> int:
        return self.state.total

    @property
    def current_index(self) -> int:
        return self.state.current_index

    @property
    def is_last(self) -> bool:
        return self.state.current_index >= self.state.total - 1

    def previous(self) -> None:
        if self.state.current_index > 0:
            self.state.current_index -= 1

    def next(self) -> None:
        if self.state.current_index < self.state.total - 1:
            self.state.current_index += 1

    # ---------- answering ----------

    async def submit(self, question_id: str, response: dict) -> None:
        await self.api.submit_answer(
            self.state.token, self.state.attempt_id, question_id, response
        )
        self.state.answers = {**self.state.answers, question_id: response}
        if self.is_last:
            await self.finish()
        else:
            self.state.current_index += 1

    async def finish(self) -> AttemptResult:
        result = await self.api.finish_attempt(self.state.token, self.state.attempt_id)
        self.state.result = result
        self.state.finished = True
        return result

    # ---------- report ----------

    async def download_report(self) -> bytes:
        return await self.api.download_report_pdf(self.state.token, self.state.attempt_id)