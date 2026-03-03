from bot.models import Homework, HomeworkScreenshots, DoneHomework, DoneHomeworkScreenshots
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

    async def create_done_homework(
            self,
            homework_id: int,
            lesson_id: int,
            student_id: int,
            done_homework_screenshots
    ):
        async with self.session_factory() as session:
            done_homework = DoneHomework(
                homework_id = homework_id,
                lesson_id = lesson_id,
                student_id = student_id
            )

            session.add(done_homework)
            await session.flush()

            if done_homework_screenshots:
                for screenshot in done_homework_screenshots:
                    new_screenshot = DoneHomeworkScreenshots(
                        done_homework_id = done_homework.id,
                        file_id = screenshot['file_id'],
                        order = screenshot['order']
                    )

                    session.add(new_screenshot)

            await session.commit()
            await session.refresh(done_homework)

            return done_homework


