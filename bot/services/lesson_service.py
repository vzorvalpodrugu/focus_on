from bot.keyboards.student_inline import back_to_student_menu, show_notify_lesson_student
from bot.services.base_service import BaseService
from aiogram import Bot
from bot.config import TG_TOKEN

class LessonService(BaseService):
    def __init__(self, lesson_repo):
        super().__init__(lesson_repo)

    async def notify_student_add_lesson(self, student_tg_id: int, teacher_name: str, subject_name: str, lesson_id: int):
        bot = Bot(token=TG_TOKEN)

        await bot.send_message(
            chat_id=student_tg_id,
            text=f"<b>👨‍🏫 Учитель {teacher_name} добавил пройденное занятие {lesson_id}🔑 по {subject_name}!✅</b>\n\n"
            "Обязательно проверьте!",
            parse_mode='HTML',
            reply_markup=await show_notify_lesson_student(lesson_id)
        )