from bot.models import Schedule, DaysEnum
from bot.services.base_service import BaseService



class ScheduleService(BaseService):
    def __init__(self, schedule_repo, subject_repo):
        super().__init__(schedule_repo)
        self.subject_repo = subject_repo

    async def get_schedule_by_user_id(self, user_id):
        return await self.repo.get_schedule_by_user_id(user_id)

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

        schedule = await self.repo.create_schedule(
            teacher_id,
            student_id,
            subject_id,
            day,
            time,
            duration,
            cost
        )

        return {
            "success": True,
            "message": "✅ Расписание успешно добавлено",
            "user": schedule
        }
