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

    def list_quizzes(self) -> list[Quiz]:
        return self.api.list_quizzes(self.state.token)

    def start(self, quiz: Quiz) -> None:
        questions = [
            self.api.get_question(self.state.token, qid) for qid in quiz.question_ids
        ]
        attempt = self.api.start_attempt(self.state.token, quiz.id)
        if not questions:
            raise ValueError("This quiz has no questions.")
        self.state.quiz = quiz
        self.state.questions = questions
        self.state.answers = {}
        self.state.attempt_id = attempt.id
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

    def submit(self, question_id: str, response: dict) -> None:
        self.api.submit_answer(
            self.state.token, self.state.attempt_id, question_id, response
        )
        idx = self.state.current_index
        self.state.answers = {**self.state.answers, idx: response}
        if self.is_last:
            self.finish()
        else:
            self.state.current_index += 1

    def finish(self) -> AttemptResult:
        result = self.api.finish_attempt(self.state.token, self.state.attempt_id)
        self.state.result = result
        self.state.finished = True
        return result