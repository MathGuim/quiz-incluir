from app.crud.base import CRUDBase
from app.models import QuizMedia
from app.schemas.media import QuizMediaCreate, QuizMediaUpdate


class CRUDQuizMedia(CRUDBase[QuizMedia, QuizMediaCreate, QuizMediaUpdate]):
    pass


quiz_media = CRUDQuizMedia(QuizMedia)
