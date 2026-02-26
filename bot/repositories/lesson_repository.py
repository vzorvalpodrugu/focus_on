from bot.repositories.base_repository import BaseRepository


class LessonRepository(BaseRepository):

    async def create_lesson(
            self,
            student_id: int,
            subject_id: int,
            teacher_id: int,
            topics: str,
            homework_id: int | None,
            screenshots: list[dict]
    ):
        pass