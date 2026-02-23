from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import F
from bot.handlers.base_handler import BaseHandler
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

            schedule = await self.schedule_service.repo.get_schedule_by_user_id(teacher.id)

            text = ''
            if schedule:
                text = '<b>Ваше расписание:</b>'
                print(schedule)
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

            await state.update_data(student_id=student_id, subject_id=subject_id)

            await callback.message.edit_text(
                '<b>Выберите день занятия:</b>',
                parse_mode='HTML',
                reply_markup=await choosing_day_keyboard()
            )






