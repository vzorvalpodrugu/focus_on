from aiogram import Bot

from bot.keyboards.student_inline import back_to_student_menu
from bot.keyboards.teacher_inline import back_to_teacher_menu_keyboard
from bot.repositories.schedule_repo import ScheduleRepository
from bot.services.lesson_service import LessonService
from bot.services.schedule_service import ScheduleService


class NotificationService:
    def __init__(self, bot: Bot, schedule_repo: ScheduleRepository):
        self.bot = bot
        self.schedule_repo = schedule_repo

    async def check_and_send_reminders(self):
        lessons = await self.schedule_repo.get_upcoming_lessons(minutes=58)

        for lesson in lessons:
            try:
                await self.bot.send_message(
                    lesson.student.tg_id,
                    f"<b>Напоминание 🔔\n\n Урок с учителем {lesson.teacher.name} 👨‍🏫 \nпо предмету {lesson.subject.name.value} 📚 \nчерез 30 минут.</b>",
                    parse_mode='HTML',
                    reply_markup= await back_to_student_menu()
                )

                await self.bot.send_message(
                    lesson.teacher.tg_id,
                    f"Напоминание 🔔\n\n Урок с учеником {lesson.student.name} 👨‍🎓 \nпо предмету {lesson.subject.name.value} 📚 \nчерез 30 минут.",
                parse_mode = 'HTML',
                reply_markup = await back_to_teacher_menu_keyboard()
                )
            except Exception as e:
                raise
