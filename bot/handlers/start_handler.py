from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.handlers.base_handler import BaseHandler
from aiogram.filters import Command
from bot.states.register import RegisterStates
from bot.keyboards.inline import role_keyboard, back_keyboard, class_number_keyboard
from aiogram import F

class StartHandler(BaseHandler):
    def __init__(self, user_service):
        self.user_service = user_service
        super().__init__()

    def _register_handlers(self):

        # 1. Команда /start
        @self.router.message(Command('start'))
        async def cmd_start(message: Message, state: FSMContext):
            await state.clear()

            user = await self.user_service.get_by_tg_id(tg_id=message.from_user.id)

            if user:
                role = 'учитель' if user.role == 'teacher' else 'ученик'
                await message.answer(
                     f"👋 С возвращением, {user.name}!\n"
                    f"Вы зарегистрированы как {role}."
                )
                return

            await state.set_state(RegisterStates.choosing_role)
            await message.answer(
                "👋 Добро пожаловать!\n\n"
                "Выберите вашу роль:",
                reply_markup=role_keyboard()
            )

        # 2. Выбор роли
        @self.router.callback_query(RegisterStates.choosing_role, F.data.startswith('role_'))
        async def process_role(callback: CallbackQuery, state: FSMContext):
            role = callback.data.replace('role_', '')

            await state.update_data(role=role)
            await state.set_state(RegisterStates.entering_name)

            await callback.message.edit_text(
                "📝 Введите ваше имя:",
                reply_markup=back_keyboard()
            )

        # 3. Выбор имени
        @self.router.message(RegisterStates.entering_name)
        async def process_name(message: Message, state: FSMContext):
            name = message.text.strip()

            if len(name) < 3:
                await message.answer('Имя слишком короткое. Попробуйте ещё раз:')
                return

            await state.update_data(name=name)
            data = await state.get_data()

            if data['role'] == 'teacher':
                await self._finish_registration(message, state)
            else:
                await state.set_state(RegisterStates.choosing_class)
                await message.answer(
                    f"📚 {name}, в каком вы классе?",
                    reply_markup=class_number_keyboard()
                )

        # 4. Выбор класса
        @self.router.callback_query(RegisterStates.choosing_class, F.data.startswith('class_'))
        async def process_class(callback: CallbackQuery, state: FSMContext):
            class_number = int(callback.data.replace('class_', ''))

            await state.update_data(class_number=class_number)
            await self._finish_registration(callback, state)

        # 5. Кнопка назад
        @self.router.callback_query(F.data == 'back_to_start')
        async def back_to_start(callback: CallbackQuery, state: FSMContext):
            await state.clear()
            await state.set_state(RegisterStates.choosing_role)
            await callback.message.edit_text(
                "👋 Выберите вашу роль:",
                reply_markup=role_keyboard()
            )

            await callback.answer()

    # 6. Завершение регистрации
    async def _finish_registration(self, target, state: FSMContext):
        data = await state.get_data()

        result = await self.user_service.register(
            tg_id=target.from_user.id,
            name=data['name'],
            class_number=data.get('class_number'),
            role=data['role']
        )

        if type(target) == CallbackQuery:
            await target.message.answer(result['message'])
        elif type(target) == Message:
            await target.answer(result['message'])

        await state.clear()