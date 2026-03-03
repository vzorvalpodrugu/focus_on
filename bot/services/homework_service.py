from bot.keyboards.student_inline import back_to_student_menu
from bot.keyboards.teacher_inline import back_to_teacher_menu_keyboard
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

    async def notify_teacher_add_done_homework(self, teacher_tg_id:int, lesson_id: int, student_name: str, subject_name:str):
        bot = Bot(token=TG_TOKEN)

        await bot.send_message(
            chat_id=teacher_tg_id,
            text=f"<b>👨‍🏫 Ученик {student_name} добавил выполненное домашнее задание к занятию {lesson_id}🔑 по {subject_name}!✅</b>\n\n"
                 "Обязательно проверьте!",
            parse_mode='HTML',
            reply_markup=await back_to_teacher_menu_keyboard()
        )