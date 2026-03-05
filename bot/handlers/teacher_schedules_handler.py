from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.teacher_inline import teacher_inline
from bot.keyboards.teacher_schedules_inline import schedule_keyboard, choosing_students_keyboard, choosing_day_keyboard
from bot.states.register_schedule import RegisterSchedule


class TeacherSchedulesHandler(BaseHandler):
    def __init__(self, schedule_service, user_service):
        super().__init__()
        self.schedule_service = schedule_service
        self.user_service = user_service

    def _register_handlers(self):

        # Показать расписание преподавателя
        @self.router.callback_query(F.data == 'show_schedules')
        async def show_schedules(callback: CallbackQuery, state: FSMContext):
            teacher_tg_id = callback.from_user.id

            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)

            await state.update_data(teacher=teacher)

            schedules = await self.schedule_service.repo.get_schedule_by_user_id(teacher.id)

            day_order = {
                "MONDAY" : 1,
                "TUESDAY": 2,
                "WEDNESDAY": 3,
                "THURSDAY": 4,
                "FRIDAY": 5,
                "SATURDAY": 6,
                "SUNDAY": 7
            }

            schedules.sort(key = lambda x: (day_order[x.day.name], x.time))

            text = ''
            if schedules:
                text = (
                    f'<b>Ваше расписание:</b>\n\n'
                )
                for schedule in schedules:
                    if schedule.link:
                        text += (f'<b>Учитель 👨‍🏫:</b> {schedule.teacher.name}\n'
                                 f'<b>Ученик 👨‍🎓:</b> {schedule.student.name}\n'
                                 f'<b>Предмет 📚:</b> {schedule.subject.name.value}\n'
                                 f'<b>День недели 📅:</b> {schedule.day.value}\n'
                                 f'<b>Время ⏰:</b> {schedule.time}\n'
                                 f'<b>Длительность ⏱️:</b> {schedule.duration}\n'
                                 f'<b>Стоимость занятия 💰:</b> {schedule.cost}\n'
                                 f'<b>Ссылка на занятие 🖥️: {schedule.link}</b>\n\n\n')
                    else:
                        text += (f'<b>Учитель 👨‍🏫:</b> {schedule.teacher.name}\n'
                                 f'<b>Ученик 👨‍🎓:</b> {schedule.student.name}\n'
                                 f'<b>Предмет 📚:</b> {schedule.subject.name.value}\n'
                                 f'<b>День недели 📅:</b> {schedule.day.value}\n'
                                 f'<b>Время ⏰:</b> {schedule.time}\n'
                                 f'<b>Длительность ⏱️:</b> {schedule.duration}\n'
                                 f'<b>Стоимость занятия 💰:</b> {schedule.cost}\n\n\n')

            else:
                text = '<b>Пока у вас нет занятий.</b>\n\nМожет Вы забыли добавить расписание учеников?'

            await callback.message.edit_text(
                text,
                parse_mode='HTML',
                reply_markup= await schedule_keyboard()
            )

        @self.router.callback_query(F.data == 'add_schedule')
        async def add_schedule(callback : CallbackQuery, state: FSMContext):
            await state.set_state(RegisterSchedule.choosing_student)
            data = await state.get_data()

            teacher = data.get('teacher')

            await callback.message.edit_text(
                '<b>Выберите ученика:</b>',
                parse_mode='HTML',
                reply_markup= await choosing_students_keyboard(teacher.id)
            )

        @self.router.callback_query(RegisterSchedule.choosing_student, F.data.startswith('stud_subj_id:'))
        async def process_student_subject(callback : CallbackQuery, state : FSMContext):
            stud_subj_id = callback.data.replace('stud_subj_id:', '')
            student_id, subject_id = stud_subj_id.split(':')

            await state.set_state(RegisterSchedule.choosing_day)

            await state.update_data(student_id=int(student_id), subject_id=int(subject_id))

            await callback.message.edit_text(
                '<b>Выберите день занятия:</b>',
                parse_mode='HTML',
                reply_markup=await choosing_day_keyboard()
            )

        @self.router.callback_query(RegisterSchedule.choosing_day, F.data.startswith('day_'))
        async def process_day(callback : CallbackQuery, state : FSMContext):
            day = callback.data.replace('day_', '')

            await state.update_data(day=day)

            await state.set_state(RegisterSchedule.choosing_time)

            await callback.message.edit_text(
                "<b>Напишите время занятия: </b>\n\n"
                "<b>В формате:</b> 14:30",
                parse_mode='HTML'
            )

        @self.router.message(RegisterSchedule.choosing_time)
        async def process_time(message: Message, state : FSMContext):
            time = message.text

            await state.set_state(RegisterSchedule.choosing_duration)

            await state.update_data(time=time)

            await message.answer(
                "<b>Напишите длительность занятия в минутах: </b>\n\n"
                "<b>Например:</b> 90",
                parse_mode='HTML',
            )

        @self.router.message(RegisterSchedule.choosing_duration)
        async def process_duration(message: Message, state: FSMContext):
            duration = int(message.text)

            await state.set_state(RegisterSchedule.choosing_cost)

            await state.update_data(duration=duration)

            await message.answer(
                "<b>Напишите стоимость занятия в рублях: </b>\n\n"
                "<b>Например:</b> 1500",
                parse_mode='HTML',
            )


        @self.router.message(RegisterSchedule.choosing_cost)
        async def process_cost(message: Message, state: FSMContext):
            cost = int(message.text)

            await state.update_data(cost=cost)

            await message.answer(
                f'<b>Вы можете приложить ссылку 🖥️ на онлайн встречу: </b>\n\n'
                f'<b>Она будет отображаться Вам и ученику перед занятием!</b>',
                parse_mode='HTML'
            )

            await state.set_state(RegisterSchedule.choosing_link)


        @self.router.message(RegisterSchedule.choosing_link)
        async def process_cost(message: Message, state: FSMContext):
            link = message.text

            await state.update_data(link=link)

            await self._finish_schedule_registration(message, state)


    async def _finish_schedule_registration(self, message: Message, state: FSMContext):
        data = await state.get_data()

        result = await self.schedule_service.create_schedule(
            teacher_id = data.get('teacher').id,
            student_id = data['student_id'],
            subject_id = data['subject_id'],
            day = data['day'],
            time = data['time'],
            duration = data['duration'],
            cost = data['cost'],
            link = data['link']
        )

        student = await self.user_service.repo.get_user_by_id(data['student_id'])
        subject = await self.schedule_service.subject_repo.get_subject_by_id(data['subject_id'])

        if result['success']:
            text = (
                f'<b>{result['message']}</b>\n\n'
                f'<b>Учитель 👨‍🏫:</b> {data.get('teacher').name}\n'
                f'<b>Ученик 👨‍🎓:</b> {student.name}\n'
                f'<b>Предмет 📚:</b> {subject.name.value}\n'
                f'<b>День недели 📅:</b> {data['day']}\n'
                f'<b>Время ⏰:</b> {data['time']}\n'
                f'<b>Длительность ⏱️:</b> {data['duration']}\n'
                f'<b>Стоимость занятия 💰:</b> {data['cost']}\n'
                f'<b>Ссылка на занятие 🖥️: {data['link']}</b>'
            )

            await self.schedule_service.notify_student_add_schedule(student_tg_id = student.tg_id, teacher_name=data.get('teacher').name)
        else:
            text = f'<b>К сожалению, что-то пошло не так :(</b>'

        await message.answer(
            text,
            parse_mode='HTML',
            reply_markup=await teacher_inline()
        )


