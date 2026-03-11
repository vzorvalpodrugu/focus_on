from aiogram import Bot

from bot.keyboards.student_inline import back_to_student_menu
from bot.keyboards.teacher_inline import back_to_teacher_menu_keyboard
from bot.repositories.schedule_repo import ScheduleRepository


class NotificationService:
    def __init__(self, bot: Bot, schedule_repo: ScheduleRepository, lesson_repo):
        self.bot = bot
        self.schedule_repo = schedule_repo
        self.lesson_repo = lesson_repo

    async def send_reminders_about_lesson(self):
        lessons = await self.schedule_repo.get_upcoming_lessons(minutes=30)

        for lesson in lessons:
            try:
                student_text, teacher_text = '', ''
                if lesson.link:
                    student_text = (
                        f"<b>Напоминание 🔔\n\n Урок с учителем 👨‍🏫:</b> {lesson.teacher.name}\n<b>Предмет 📚: </b>{lesson.subject.name.value}\n<b>Через 30 минут ⏰</b>\n\n"
                        f"<b>Ссылка на занятие 📺: </b>\n{lesson.link}"
                    )
                    teacher_text = (
                        f"<b>Напоминание 🔔\n\n Урок с учеником 👨‍🎓:</b> {lesson.student.name}\n<b>Предмет 📚: </b>{lesson.subject.name.value}\n<b>Через 30 минут ⏰\n\n</b>"
                        f"<b>Ссылка на занятие 📺: </b>\n{lesson.link}"
                    )
                else:
                    student_text = (
                        f"<b>Напоминание 🔔\n\n Урок с учителем 👨‍🏫:</b> {lesson.teacher.name}\n<b>Предмет 📚: </b>{lesson.subject.name.value}\n<b>Через 30 минут ⏰</b>\n\n"
                    )
                    teacher_text = (
                        f"<b>Напоминание 🔔\n\n Урок с учеником 👨‍🎓:</b> {lesson.student.name}\n<b>Предмет 📚: </b>{lesson.subject.name.value}\n<b>Через 30 минут ⏰\n\n</b>"
                    )

                await self.bot.send_message(
                    lesson.student.tg_id,
                    student_text,
                    parse_mode='HTML',
                    reply_markup= await back_to_student_menu()
                )

                await self.bot.send_message(
                    lesson.teacher.tg_id,
                    teacher_text,
                    parse_mode = 'HTML',
                    reply_markup = await back_to_teacher_menu_keyboard()
                )
            except Exception as e:
                raise

    async def send_reminders_about_homework(self):
        schedules = await self.schedule_repo.get_upcoming_lessons(minutes=180)

        for schedule in schedules:
            teacher_id = schedule.teacher.id
            student_id = schedule.student.id
            subject_id = schedule.subject.id

            try:
                lessons = await self.lesson_repo.get_lessons(
                    teacher_id = teacher_id,
                    student_id = student_id,
                    subject_id = subject_id,
                )

                for lesson in lessons:

                    if lesson.done_homework is None:
                        await self.bot.send_message(
                            lesson.student.tg_id,
                            f"<b>Напоминание 🔔\n\n К ближайшему занятию по {lesson.subject.name.value} 📚 у вас не выполнено ДЗ 📓!\n\n</b>"
                            f"<b>Поспешите выполнить и отправить!</b>",
                            parse_mode='HTML',
                            reply_markup=await back_to_student_menu()
                        )

            except Exception as e:
                raise
