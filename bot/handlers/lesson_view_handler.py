from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram import F, Bot

from bot.handlers.base_handler import BaseHandler
from bot.keyboards.lesson_view_inline import choosing_period_keyboard, choice_at_next_lesson_keyboard
from bot.keyboards.student_inline import back_to_student_menu
from bot.config import TG_TOKEN
from bot.states.lesson_view_states import LessonViewStates


class LessonViewHandler(BaseHandler):
    def __init__(self, lesson_service, user_service, homework_service):
        super().__init__()
        self.lesson_service = lesson_service
        self.user_service = user_service
        self.homework_service = homework_service

    def _register_handlers(self):

        # ------------------------------------------------------
        # Отображение занятий
        # ------------------------------------------------------

        @self.router.callback_query(F.data == 'show_lessons')
        # 1. Выбор периода
        async def process_lessons(callback: CallbackQuery, state: FSMContext):
            user_tg_id = callback.from_user.id
            user = await self.user_service.get_by_tg_id(user_tg_id)

            await state.update_data(user=user)
            await state.set_state(LessonViewStates.choosing_period)

            text = f"<b>{user.name}, выберите период ⌛, в котором хотите посмотреть занятия.</b>"

            if user.role == 'student' or user.role == 'teacher':
                await callback.message.edit_text(
                    text,
                    parse_mode='HTML',
                    reply_markup=await choosing_period_keyboard(user.role)
                )


        @self.router.callback_query(LessonViewStates.choosing_period, F.data.startswith('period_'))
        async def process_period(callback: CallbackQuery, state: FSMContext):
            # 2. Обработка периода
            period = callback.data.replace('period_', '')

            data = await state.get_data()
            user = data.get('user')

            lessons = await self.lesson_service.repo.get_lessons_by_period(user_id=user.id, role=user.role, period_type=period)

            for lesson in lessons:
                await callback.message.answer(
                    f"<b>id занятия 🔑: </b>{lesson.id}\n\n"
                    f"<b>Учитель 👨‍🏫:</b> {lesson.teacher.name} \n"
                    f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                    f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                    f"<b>Тема 📝: </b>{lesson.topics}\n\n"
                    f'<b>Дата 📅: </b>{lesson.created_at}',
                    parse_mode='HTML'
                )

            await callback.message.answer(
                f"<b>Отправьте id занятия 🔑, которое хотели бы посмотреть!</b>",
                parse_mode='HTML',
                reply_markup=await back_to_student_menu()
            )

            await state.set_state(LessonViewStates.choosing_lesson_id)

        @self.router.message(LessonViewStates.choosing_lesson_id)
        async def process_lesson_id(message: Message, state: FSMContext):
            # 3. Отображение урока
            lesson_id = int(message.text)
            user = (await state.get_data()).get('user')

            bot = Bot(token=TG_TOKEN)

            if lesson_id < 0 or type(lesson_id) is not int:
                return

            lesson = await self.lesson_service.repo.get_lesson_by_id(lesson_id=lesson_id)

            lesson_media_group = [
                InputMediaPhoto(media=screenshot.file_id)
                for screenshot in lesson.lesson_screenshots
            ]
            await message.answer(
                f'<b>Конспект 📝:</b>',
                parse_mode='HTML'
            )
            if lesson_media_group:
                await bot.send_media_group(
                    chat_id=message.chat.id,
                    media=lesson_media_group
                )

            if lesson.homework:

                homework_media_group = [
                    InputMediaPhoto(media=screenshot.file_id)
                    for screenshot in lesson.homework.homework_screenshots
                ]

                await message.answer(
                    f'<b>Домашнее задание 📓:</b>',
                    parse_mode='HTML'
                )

                if homework_media_group:
                    await bot.send_media_group(
                        chat_id=message.chat.id,
                        media=homework_media_group
                    )

            await message.answer(
                text = '<b>Выберите действие 💬:</b>',
                parse_mode='HTML',
                reply_markup=await choice_at_next_lesson_keyboard(role=user.role)
            )

        @self.router.callback_query(LessonViewStates.choosing_lesson_id, F.data == 'show_one_more_lesson')
        async def process_one_more_lesson(callback: CallbackQuery):
            await callback.message.edit_text(
                f"<b>Отправьте id занятия 🔑, которое хотели бы посмотреть!</b>",
                parse_mode='HTML',
                reply_markup=await back_to_student_menu()
            )




