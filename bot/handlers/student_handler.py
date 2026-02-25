from aiogram.types import CallbackQuery
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.student_inline import student_inline, back_to_student_menu


class StudentHandler(BaseHandler):
    def __init__(self, user_service, schedule_service):
        super().__init__()
        self.user_service = user_service
        self.schedule_service = schedule_service


    def _register_handlers(self):


        @self.router.callback_query(F.data == 'back_to_student_menu')
        async def process_back(callback : CallbackQuery):
            user_tg_id = callback.from_user.id
            user = await self.user_service.repo.get_by_tg_id(user_tg_id)

            await callback.message.edit_text(
                f'<b>{user.name}</b> 💬\n\nВыберите действие:\n\n',
                parse_mode='HTML',
                reply_markup=await student_inline()
            )


        @self.router.callback_query(F.data == 'show_profile')
        async def process_profile(callback : CallbackQuery):
            user_tg_id = callback.from_user.id

            user = await self.user_service.repo.get_by_tg_id(user_tg_id)
            subjects = await self.user_service.user_subject_repo.get_user_subjects(user.id)

            subject_text = ''

            for subject in subjects:
                subject_text += f'{subject.name.value}, '

            text = (
                f'<b>👤 Ваш профиль: </b> \n\n'
                
                f'<b>Имя 🧑: </b>{user.name}\n'
                f'<b>Класс 📚: </b>{user.class_number}\n'
                f'<b>Статус 👨‍🎓: </b>{user.role.value}\n'
                f'<b>Предметы ⚙️: </b>{subject_text[:-2]}\n'
            )

            await callback.message.edit_text(
                text=text,
                parse_mode='HTML',
                reply_markup=await back_to_student_menu()
            )

        @self.router.callback_query(F.data == 'show_students_schedule')
        async def process_schedule(callback : CallbackQuery):
            user_tg_id = callback.from_user.id
            user = await self.user_service.repo.get_by_tg_id(user_tg_id)

            schedules = await self.schedule_service.repo.get_schedule_by_user_id(user.id)

            day_order = {
                "MONDAY": 1,
                "TUESDAY": 2,
                "WEDNESDAY": 3,
                "THURSDAY": 4,
                "FRIDAY": 5,
                "SATURDAY": 6,
                "SUNDAY": 7
            }

            text = ''
            if schedules:
                schedules.sort(key=lambda x: (day_order[x.day.name], x.time))

                text = (
                    f'<b>Ваше расписание:</b>\n\n'
                )

                for schedule in schedules:
                    text += (f'<b>Учитель 👨‍🏫:</b> {schedule.teacher.name}\n'
                             f'<b>Ученик 👨‍🎓:</b> {schedule.student.name}\n'
                             f'<b>Предмет 📚:</b> {schedule.subject.name.value}\n'
                             f'<b>День недели 📅:</b> {schedule.day.value}\n'
                             f'<b>Время ⏰:</b> {schedule.time}\n'
                             f'<b>Длительность ⏱️:</b> {schedule.duration}\n\n\n')
            else:
                text = '<b>Пока у вас нет занятий.</b>\n\nОжидайте, когда преподаватель обновит расписание.\nВам придёт уведомление!'


            await callback.message.edit_text(
                text=text,
                parse_mode = 'HTML'
            )

            await callback.message.answer(
                f'<b>{user.name}</b> 💬\n\nВыберите действие:\n\n',
                parse_mode='HTML',
                reply_markup=await student_inline()
            )
