from bot.models import Schedule, User, Subject, DaysEnum
from bot.repositories.base_repository import BaseRepository
from sqlalchemy import or_, and_, select

class ScheduleRepository(BaseRepository):

    async def create_schedule(
            self,
            teacher_id: int,
            student_id: int,
            subject_id: int,
            day: DaysEnum,
            time: str,
            duration: int,
            cost: int
    ):
        async with self.session_factory() as session:
            schedule = Schedule(
                teacher_id = teacher_id,
                student_id = student_id,
                subject_id = subject_id,
                day = day,
                time = time,
                duration = duration,
                cost = cost
            )
            session.add(schedule)
            await session.commit()

            return schedule

    async def get_schedule_by_user_id(self, user_id: int):
        # Получить расписание по id пользователя
        async with self.session_factory() as session:
            result = await session.execute(
                select(Schedule)
                .where(
                    or_(
                        Schedule.teacher_id == user_id,
                        Schedule.student_id == user_id,
                    )
                )
            )

            return list(result.scalars().all())

