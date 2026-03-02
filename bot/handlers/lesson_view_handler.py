from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.lesson_view_inline import choosing_period_keyboard
from bot.states.lesson_view_states import LessonViewStates


class LessonViewHandler(BaseHandler):
    def __init__(self, lesson_service, user_service, homework_service):
        super().__init__()
        self.lesson_service = lesson_service
        self.user_service = user_service
        self.homework_service = homework_service

    def _register_handlers(self):

        @self.router.callback_query(F.data == 'show_lessons')
        async def process_lessons(callback: CallbackQuery, state: FSMContext):
            user_tg_id = callback.from_user.id
            user = await self.user_service.get_by_tg_id(user_tg_id)

            await state.update_data(user=user)
            await state.set_state(LessonViewStates.choosing_period)

            text = f"<b>{user.name}, выберите период ⌛, в котором хотите посмотреть занятия.</b>"

            if user.role == 'student' or user.role == 'teacher':
                await callback.message.answer(
                    text,
                    parse_mode='HTML',
                    reply_markup=await choosing_period_keyboard(user.role)
                )
        @self.router.callback_query(LessonViewStates.choosing_period, F.data.startswith('period_'))
        async def process_period(callback: CallbackQuery, state: FSMContext):
            period = callback.data.replace('period_', '')




