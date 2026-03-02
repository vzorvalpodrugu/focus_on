from bot.models import Homework, HomeworkScreenshots
from bot.repositories.base_repository import BaseRepository


class HomeworkRepository(BaseRepository):

    async def create_homework(
            self,
            student_id: int,
            subject_id: int,
            teacher_id: int,
            homework_screenshots : list[dict] | None,
            topics: str
    ):
        async with self.session_factory() as session:
            homework = Homework(
                student_id = student_id,
                subject_id = subject_id,
                teacher_id = teacher_id,
                topics = topics
            )

            session.add(homework)
            await session.flush()
            if homework_screenshots:
                for screenshot in homework_screenshots:
                    new_screenshot = HomeworkScreenshots(
                        homework_id = homework.id,
                        file_id = screenshot['file_id'],
                        order = screenshot['order']
                    )

                    session.add(new_screenshot)

            await session.commit()
            await session.refresh(homework)

            return homework


