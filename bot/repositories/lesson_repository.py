from bot.models import Lesson, LessonScreenshots
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
        async with self.session_factory() as session:

            lesson = Lesson(
                student_id = student_id,
                subject_id = subject_id,
                teacher_id = teacher_id,
                topics = topics
            )

            session.add(lesson)
            await session.flush()

            for screenshot in screenshots:
                new_screenshot = LessonScreenshots(
                    lesson_id = lesson.id,
                    file_id = screenshot['file_id'],
                    order = screenshot['order']
                )
                session.add(new_screenshot)



            await session.commit()
            await session.refresh(lesson)

            return lesson



