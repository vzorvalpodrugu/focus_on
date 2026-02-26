from bot.services.base_service import BaseService


class LessonService(BaseService):
    def __init__(self, lesson_repo):
        super().__init__(lesson_repo)
