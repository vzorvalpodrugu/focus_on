from aiogram import Bot

from bot.keyboards.student_inline import back_to_student_menu
from bot.models import DaysEnum
from bot.services.base_service import BaseService
from bot.config import TG_TOKEN


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

    async def notify_student_add_schedule(self, student_tg_id: int, teacher_name: str):
        bot = Bot(token=TG_TOKEN)

        await bot.send_message(
            chat_id=student_tg_id,
            text=f"<b>👨‍🏫 Учитель {teacher_name} добавил новое занятие в расписание!✅</b>\n\n"
            "Обязательно проверьте!",
            parse_mode='HTML',
            reply_markup=await back_to_student_menu()
        )


