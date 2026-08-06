from app.crud.base import CRUDBase
from app.models import QuestionMedia
from app.schemas.media import MediaCreate, MediaUpdate


class CRUDMedia(CRUDBase[QuestionMedia, MediaCreate, MediaUpdate]):
    pass


media = CRUDMedia(QuestionMedia)
