from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.config import actual_teacher_tg_ids
from bot.database import async_session_maker
from bot.handlers.base_handler import BaseHandler
from aiogram.filters import Command

from bot.keyboards.teacher_inline import teacher_inline
from bot.keyboards.student_inline import student_inline
from bot.repositories.subject_repository import SubjectRepository
from bot.states.register import RegisterStates
from bot.keyboards.inline import role_keyboard, back_keyboard, class_number_keyboard, subjects_keyboard
from aiogram import F

class StartHandler(BaseHandler):
    def __init__(self, user_service):
        self.user_service = user_service
        super().__init__()

    # Функция получения имен предметов по id
    @staticmethod
    async def get_subjects_name(state: FSMContext):
        data = await state.get_data()
        subj_ids = data.get('selected_subjects')

        if not subj_ids:
            subj_ids = []

        subj_repo = SubjectRepository(async_session_maker)
        subjects = await subj_repo.get_by_ids(subj_ids)

        subject_names = [str(subj.name.value) for subj in subjects]

        return subject_names

    def _register_handlers(self):

        # 1. Команда /start
        @self.router.message(Command('start'))
        async def cmd_start(message: Message, state: FSMContext):
            await state.clear()

            user = await self.user_service.get_by_tg_id(tg_id=message.from_user.id)


            if user:
                role = 'учитель' if user.role == 'teacher' else 'ученик'

                keyboard = await teacher_inline() if user.role == 'teacher' else await student_inline()
                await message.answer(
                     f"<b>Приветствую 👋, </b>{user.name}!\n"
                    f"<b>Вы зарегистрированы как </b> {role}"
                    f"<b>Выберите действие: 💬</b>",
                    parse_mode = 'HTML',
                    reply_markup=keyboard
                )
                return

            await state.set_state(RegisterStates.choosing_role)
            await message.answer(
                "<b>👋 Добро пожаловать!</b>\n\n"
                "<b>Выберите вашу роль:</b>",
                parse_mode='HTML',
                reply_markup=role_keyboard()
            )

        # 2. Выбор роли
        @self.router.callback_query(RegisterStates.choosing_role, F.data.startswith('role_'))
        async def process_role(callback: CallbackQuery, state: FSMContext):
            role = callback.data.replace('role_', '')
            user_tg_id = callback.from_user.id

            if role == 'teacher' and user_tg_id not in actual_teacher_tg_ids:
                await state.set_state(RegisterStates.choosing_role)
                await callback.message.answer(
                    "<b>К сожалению, вы не можете зарегистрироваться учителем 🚫</b>\n"
                    "<b>Уточните в поддержке!\n\n</b>"
                    "Выберите вашу роль:",
                    parse_mode='HTML',
                    reply_markup=role_keyboard()
                )
                return

            await state.update_data(role=role)
            await state.set_state(RegisterStates.entering_name)

            await callback.message.edit_text(
                "<b>📝 Введите ваше имя:</b>",
                parse_mode = 'HTML',
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
            if data['role'] == 'student':
                await state.set_state(RegisterStates.choosing_class)
                await message.answer(
                    f"📚 {name}, в каком вы классе?",
                    parse_mode = 'HTML',
                    reply_markup=class_number_keyboard()
                )
            elif data['role'] == 'teacher':
                await state.set_state(RegisterStates.choosing_subjects)
                await message.answer(
                    f"📚 {name}, выберите, какие предметы Вы будете преподавать?",
                    parse_mode = 'HTML',
                    reply_markup=await subjects_keyboard()
                )


        # 4. Выбор класса
        @self.router.callback_query(RegisterStates.choosing_class, F.data.startswith('class_'))
        async def process_class(callback: CallbackQuery, state: FSMContext):
            class_number = int(callback.data.replace('class_', ''))
            await state.update_data(class_number=class_number)
            data = await state.get_data()

            await state.set_state(RegisterStates.choosing_subjects)

            await callback.message.answer(
                f"📚 {data['name']}, выберите, какие предметы будете изучать с преподавателем?",
                reply_markup= await subjects_keyboard()
            )


        # 5. Выбор предмета
        @self.router.callback_query(RegisterStates.choosing_subjects, F.data.startswith('subject_'))
        async def process_subject(callback: CallbackQuery, state: FSMContext):
            subject_id = int(callback.data.replace('subject_', ''))

            data = await state.get_data()
            selected = data.get('selected_subjects', [])

            if subject_id in selected:
                selected.remove(subject_id)
            else:
                selected.append(subject_id)

            await state.update_data(selected_subjects=selected)

            # 👇 Передаём обновлённый список В КЛАВИАТУРУ
            await callback.message.edit_reply_markup(
                reply_markup=await subjects_keyboard(selected)
            )

        # 6. Выбор предметов завершен subjects_done
        @self.router.callback_query(RegisterStates.choosing_subjects, F.data.startswith('subjects_done'))
        async def process_subject_done(callback: CallbackQuery, state: FSMContext):
            await self._finish_registration(callback, state)


        # 7. Кнопка назад
        @self.router.callback_query(F.data == 'back_to_start')
        async def back_to_start(callback: CallbackQuery, state: FSMContext):
            await state.clear()
            await state.set_state(RegisterStates.choosing_role)
            await callback.message.edit_text(
                "👋 Выберите вашу роль:",
                reply_markup=role_keyboard()
            )

            await callback.answer()

    # 7. Завершение регистрации
    async def _finish_registration(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()

        result = await self.user_service.register(
            tg_id=callback.from_user.id,
            name=data['name'],
            class_number=data.get('class_number'),
            role=data['role'],
            subject_ids=data.get('selected_subjects')
        )

        subjects_name = await self.get_subjects_name(state=state)

        result_subjects_name = ''
        for subj in subjects_name:
            result_subjects_name += subj + " "

        if data['role'] == 'student':
            await callback.message.answer(
                f'<b>{result['message']}</b>' +
                '\n\n📋 <b>Ваш профиль:</b>'
                f"\n👤 <b>Имя:</b> {data['name']}"
                f"\n🎭 <b>Статус:</b> 👨‍🎓 {data['role']}"
                f"\n📚 <b>Класс:</b> {data.get('class_number')}"
                f"\n📖 <b>Предметы:</b> {result_subjects_name}",
                parse_mode='HTML'
            )

            await callback.message.answer(
                f'<b>{data['name']}</b> 💬\n\nВыберите действие:\n\n',
                parse_mode='HTML',
                reply_markup=await student_inline()
            )

        elif data['role'] == 'teacher':
            await callback.message.answer(
                f'<b>{result['message']}</b>' +
                '\n\n📋 <b>Ваш профиль:</b>'
                f"\n👤 <b>Имя:</b> {data['name']}"
                f"\n🎭 <b>Статус:</b> 👨‍🎓 {data['role']}"
                f"\n📖 <b>Предметы:</b> {result_subjects_name}",
                parse_mode='HTML',
            )
            await callback.message.answer(
                f'<b>{data['name']}</b> 💬\n\nВыберите действие:\n\n',
                parse_mode='HTML',
                reply_markup = await teacher_inline()
            )


        await state.clear()