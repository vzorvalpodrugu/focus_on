from bot.keyboards.student_inline import back_to_student_menu
from bot.services.base_service import BaseService
from aiogram import Bot
from bot.config import TG_TOKEN

class HomeworkService(BaseService):
    def __init__(self, homework_repo):
        super().__init__(homework_repo)


    async def notify_student_add_homework(self, student_tg_id: int, teacher_name: str, subject_name: str, lesson_id: int):
        bot = Bot(token=TG_TOKEN)

        await bot.send_message(
            chat_id=student_tg_id,
            text=f"<b>👨‍🏫 Учитель {teacher_name} добавил домашнее задание к занятию {lesson_id}🔑 по {subject_name}!✅</b>\n\n"
            "Обязательно проверьте!",
            parse_mode='HTML',
            reply_markup=await back_to_student_menu()
        )