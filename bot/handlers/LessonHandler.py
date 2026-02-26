from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.create_lesson_inline import choosing_student_keyboard, choosing_subject_keyboard, \
    screenshots_done_keyboard, homework_done_keyboard
from bot.keyboards.teacher_inline import back_to_teacher_menu_keyboard
from bot.states.register_lesson import RegisterLesson


class LessonHandler(BaseHandler):
    def __init__(self, lesson_service, user_service):
        super().__init__()
        self.lesson_service = lesson_service
        self.user_service = user_service


    def _register_handlers(self):

        @self.router.callback_query(F.data == 'create_lesson')
        async def process_create(callback : CallbackQuery, state : FSMContext):
            # 1. Выбор студента
            teacher_tg_id = callback.from_user.id

            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)

            await state.update_data(teacher=teacher)

            await state.set_state(RegisterLesson.choosing_student)

            await callback.message.edit_text(
                '<b>Выберите ученика 👨‍🎓, с которым у вас урок: </b>',
                parse_mode='HTML',
                reply_markup=await choosing_student_keyboard(teacher_id=teacher.id)
            )

        @self.router.callback_query(RegisterLesson.choosing_student, F.data.startswith('student_'))
        async def process_student(callback : CallbackQuery, state : FSMContext):
            # 2. Выбор предмета
            student_id = int(callback.data.replace('student_', ''))

            student = self.user_service.repo.get_user_by_id(student_id)

            await state.update_data(student=student)
            data = await state.get_data()
            teacher_id = data.get('teacher').id

            await state.set_state(RegisterLesson.choosing_subject)

            await callback.message.edit_text(
                f'<b>Выберите предмет 📚, по которому у вас занятие: </b>',
                parse_mode='HTML',
                reply_markup=await choosing_subject_keyboard(teacher_id=teacher_id, student_id=student_id)
            )

        @self.router.callback_query(RegisterLesson.choosing_subject, F.data.startswith('subject_'))
        async def process_subject(callback : CallbackQuery, state : FSMContext):
            # 3. Запись темы
            subject_id = int(callback.data.replace('subject_', ''))

            subject = await self.user_service.subject_repo.get_subject_by_id(subject_id)

            await state.update_data(subject=subject)

            await state.set_state(RegisterLesson.choosing_topic)

            await callback.message.edit_text(
                f'<b>Запишите тему сегодняшнего урока ✏️:</b>\n\n'
                f'<b>Например :</b> 2. Квадратные уравнения',
                parse_mode='HTML',
                reply_markup= await back_to_teacher_menu_keyboard()
            )

        @self.router.message(RegisterLesson.choosing_topic)
        async def process_subject(message: Message, state: FSMContext):
            # 4. Создание конспекта
            topic = message.text

            await state.update_data(topic=topic)

            await state.set_state(RegisterLesson.waiting_for_lesson_screenshots)

            await message.answer(
                f'<b>Пришлите конспект 📝 занятия в виде скриншотов: </b>\n\n'
                f'<b>Можно прислать сразу несколько!</b>',
                parse_mode='HTML',
                reply_markup= await back_to_teacher_menu_keyboard()
            )

        @self.router.message(RegisterLesson.waiting_for_lesson_screenshots, F.media_group)
        async def process_screenshots_album(message: Message, state: FSMContext, album: list[Message]):
            """Обработка пачки скринов (альбом)"""

            screenshots = []

            for msg in album:
                if msg.photo:
                    file_id = msg.photo[-1].file_id
                    screenshots.append({
                        'file_id': file_id,
                        'file_type': 'photo'
                    })
                elif msg.document and msg.document.mime_type.startswith('image/'):
                    file_id = msg.document.file_id
                    screenshots.append({
                        'file_id': file_id,
                        'file_type': 'document'
                    })

            if not screenshots:
                await message.answer("❌ В альбоме нет изображений")
                return

            # Получаем текущие скрины
            data = await state.get_data()
            existing = data.get('screenshots', [])

            # Добавляем новые с правильным порядком
            start_order = len(existing) + 1
            for i, scr in enumerate(screenshots, start=start_order):
                scr['order'] = i
                existing.append(scr)

            await state.update_data(screenshots=existing)

            await message.answer(
                f"✅ Добавлено {len(screenshots)} скриншотов!\n"
                f"Всего: {len(existing)}\n\n"
                f"Можете добавить ещё или нажать 'Готово'",
                reply_markup=await screenshots_done_keyboard()
            )

        @self.router.message(RegisterLesson.waiting_for_lesson_screenshots, F.photo | F.document)
        async def process_single_screenshot(message: Message, state: FSMContext):
            """Обработка одиночного скриншота"""

            # Получаем file_id
            if message.photo:
                file_id = message.photo[-1].file_id
                file_type = 'photo'
            elif message.document and message.document.mime_type.startswith('image/'):
                file_id = message.document.file_id
                file_type = 'document'
            else:
                await message.answer("❌ Пожалуйста, отправьте изображение")
                return

            data = await state.get_data()
            screenshots = data.get('screenshots', [])

            screenshots.append({
                'file_id': file_id,
                'order': len(screenshots) + 1,
                'file_type': file_type
            })

            await state.update_data(screenshots=screenshots)

            await message.answer(
                f"✅ Скриншот {len(screenshots)} добавлен!\n"
                f"Отправьте ещё или нажмите 'Готово'",
                reply_markup=await screenshots_done_keyboard()
            )

        @self.router.callback_query(RegisterLesson.waiting_for_lesson_screenshots, F.data == 'create_homework')
        async def process_homework(callback: CallbackQuery, state: FSMContext):
            await state.set_state(RegisterLesson.waiting_for_homework)

            await callback.message.answer(
                f'<b>Конспект сформирован! ✅</b>\n\n'
                f'<b>Осталось добавить домашнее задание 🖊️!</b>\n'
                f'<b>Если хотите отправить его позже, то нажмите Готово ✅</b>',
                parse_mode='HTML',
                reply_markup=await homework_done_keyboard()
            )

        @self.router.callback_query(RegisterLesson.waiting_for_homework, F.data == 'finish_lesson')
        async def process_finish(callback: CallbackQuery, state: FSMContext):

            return await self._finish_create_lesson(callback, state)


    async def _finish_create_lesson(self, callback, state):
        pass