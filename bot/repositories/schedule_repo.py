import pytz
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta
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
            cost: int,
            link: str | None
    ):
        async with self.session_factory() as session:
            schedule = Schedule(
                teacher_id = teacher_id,
                student_id = student_id,
                subject_id = subject_id,
                day = day,
                time = time,
                duration = duration,
                cost = cost,
                link = link
            )
            session.add(schedule)
            await session.commit()

            return schedule

    async def get_schedule_by_user_id(self, user_id: int):
        # Получить расписание по id пользователя
        async with self.session_factory() as session:
            result = await session.execute(
                select(Schedule)
                .options(
                    selectinload(Schedule.teacher),
                    selectinload(Schedule.student),
                    selectinload(Schedule.subject),
                )
                .where(
                    or_(
                        Schedule.teacher_id == user_id,
                        Schedule.student_id == user_id,
                    )
                )
            )

            return list(result.scalars().all())

    async def get_upcoming_lessons(self, minutes: int = 30):
        # 1. Устанавливаем московскую временную зону
        moscow_tz = pytz.timezone('Europe/Moscow')

        # 2. Получаем "сейчас" именно в Москве
        now_moscow = datetime.now(moscow_tz)

        # 3. Вычисляем целевое время (через 30 минут)
        target_datetime = now_moscow + timedelta(minutes=minutes)
        target_time_str = target_datetime.strftime("%H:%M")

        # 4. Определяем день недели для Москвы
        days_map = {
            0: DaysEnum.MONDAY,
            1: DaysEnum.TUESDAY,
            2: DaysEnum.WEDNESDAY,
            3: DaysEnum.THURSDAY,
            4: DaysEnum.FRIDAY,
            5: DaysEnum.SATURDAY,
            6: DaysEnum.SUNDAY
        }
        current_day_enum = days_map[now_moscow.weekday()]

        async with self.session_factory() as session:
            query = (
                select(Schedule)
                .where(
                    Schedule.day == current_day_enum,
                    Schedule.time == target_time_str
                )
                .options(
                    joinedload(Schedule.teacher),
                    joinedload(Schedule.student),
                    joinedload(Schedule.subject)
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

