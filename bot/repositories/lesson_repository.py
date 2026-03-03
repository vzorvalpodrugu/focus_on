from datetime import datetime, timedelta

from sqlalchemy.orm import selectinload

from bot.models import Lesson, LessonScreenshots, Homework, DoneHomework
from bot.repositories.base_repository import BaseRepository
from sqlalchemy import update, select, and_, or_, exists


class LessonRepository(BaseRepository):

    async def get_lesson_by_id(self, lesson_id: int) -> Lesson:
        # Получить lesson по lesson_id
        async with self.session_factory() as session:
            result = await session.execute(
                select(Lesson)
                .options(
                    selectinload(Lesson.teacher),
                    selectinload(Lesson.student),
                    selectinload(Lesson.subject),
                    selectinload(Lesson.homework).selectinload(Homework.homework_screenshots),
                    selectinload(Lesson.lesson_screenshots)
                )
                .where(Lesson.id == lesson_id)
            )

            return result.scalar_one_or_none()


    async def create_lesson(
            self,
            student_id: int,
            subject_id: int,
            teacher_id: int,
            topics: str,
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

    async def update_lesson_homework(self, lesson_id: int, homework_id: int):
        async with self.session_factory() as session:
            query = (
                update(Lesson)
                .where(Lesson.id == lesson_id)
                .values(homework_id=homework_id)
            )
            await session.execute(query)
            await session.commit()

    async def get_lessons_without_hw(self, teacher_id: int) -> list[Lesson]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Lesson)
                .options(
                    selectinload(Lesson.teacher),
                    selectinload(Lesson.student),
                    selectinload(Lesson.subject)
                )
                .where(
                    and_(
                        Lesson.teacher_id == teacher_id,
                        Lesson.homework_id == None
                    )
                )
            )

            return list(result.scalars().all())

    async def get_lessons_without_done_hw(self, user_id: int) -> list[Lesson]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Lesson)
                .options(
                    selectinload(Lesson.teacher),
                    selectinload(Lesson.student),
                    selectinload(Lesson.subject),
                    selectinload(Lesson.homework).selectinload(Homework.homework_screenshots)
                )
                .where(
                    and_(
                        or_(
                            Lesson.student_id == user_id,
                            Lesson.teacher_id == user_id
                        ),
                        Lesson.homework_id.isnot(None),  # ДЗ прикреплено
                        ~exists().where(  # НЕТ записи в done_homeworks
                            DoneHomework.lesson_id == Lesson.id
                        )
                    )
                )
            )
            return list(result.scalars().all())


    async def get_lessons_by_period(
            self,
            user_id: int,
            role: str,
            period_type: str  # '2weeks', 'all', или номер месяца '1'..'12'
    ) -> list[Lesson]:
        """Получить занятия по роли и периоду"""

        async with self.session_factory() as session:
            query = select(Lesson).options(
                selectinload(Lesson.teacher),
                selectinload(Lesson.student),
                selectinload(Lesson.subject)
            )

            # Фильтр по роли
            if role == 'teacher':
                query = query.where(Lesson.teacher_id == user_id)
            else:  # student
                query = query.where(Lesson.student_id == user_id)

            now = datetime.now()

            # Фильтр по периоду
            if period_type == '2weeks':
                two_weeks_ago = now - timedelta(days=14)
                query = query.where(Lesson.created_at >= two_weeks_ago)

            elif period_type.isdigit():  # если это число (месяц)
                month = int(period_type)
                year = now.year

                # Начало месяца
                start_date = datetime(year, month, 1)

                # Конец месяца
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)

                query = query.where(Lesson.created_at.between(start_date, end_date))
            elif period_type == 'last':
                query = query.order_by(Lesson.created_at.desc()).limit(1)


            # period_type == 'all' — без фильтра по дате

            query = query.order_by(Lesson.created_at.desc())
            result = await session.execute(query)

            return list(result.scalars().all())




