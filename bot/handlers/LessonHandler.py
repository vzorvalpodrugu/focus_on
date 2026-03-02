from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.create_lesson_inline import choosing_student_keyboard, choosing_subject_keyboard, \
    screenshots_done_keyboard, homework_from_lesson_create_done_keyboard, choose_homework_keyboard, \
    homework_done_keyboard
from bot.keyboards.teacher_inline import back_to_teacher_menu_keyboard, teacher_inline
from bot.states.register_homework import RegisterHomework
from bot.states.register_lesson import RegisterLesson


class LessonHandler(BaseHandler):
    def __init__(self, lesson_service, user_service, homework_service):
        super().__init__()
        self.lesson_service = lesson_service
        self.user_service = user_service
        self.homework_service = homework_service

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

            student = await self.user_service.repo.get_user_by_id(student_id)

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

        @self.router.message(RegisterLesson.waiting_for_lesson_screenshots, F.photo)
        async def process_screenshots(message: Message, state: FSMContext, album: list[Message] = None):
            # Определяем источник фото: список из альбома или одиночное сообщение
            media_to_process = album if album else [message]

            screenshots_to_add = []
            for msg in media_to_process:
                if msg.photo:
                    file_id = msg.photo[-1].file_id
                    screenshots_to_add.append({'file_id': file_id})

            if not screenshots_to_add:
                return await message.answer("❌ Не удалось распознать фото.")

            # Логика сохранения в FSM
            data = await state.get_data()
            existing = data.get('screenshots', [])

            start_order = len(existing) + 1
            for i, scr in enumerate(screenshots_to_add, start=start_order):
                scr['order'] = i
                existing.append(scr)

            await state.update_data(screenshots=existing)

            # Формируем ответ
            added_count = len(screenshots_to_add)
            total = len(existing)

            if added_count > 1:
                text = f"✅ Добавлено {added_count} скриншотов!\nВсего: {total}"
            else:
                text = f"✅ Скриншот {total} добавлен!"

            text += "\n\nМожете добавить ещё или нажмите 'Готово'"

            # Отвечаем на последнее сообщение (или единственное)
            await message.answer(
                text,
                reply_markup=await screenshots_done_keyboard()
            )


        @self.router.callback_query(RegisterLesson.waiting_for_lesson_screenshots, F.data == 'wanna_homework')
        async def process_choose_homework(callback: CallbackQuery, state: FSMContext):
            # 6. Добавить ли домашку?
            await callback.message.edit_text(
                "<b>Хотите ли вы добавить домашнее задание 🖊️?</b>",
                parse_mode = 'HTML',
                reply_markup=await choose_homework_keyboard()
            )

        @self.router.callback_query(RegisterLesson.waiting_for_lesson_screenshots, F.data == 'create_homework')
            # 7. Если ответ да!
        async def process_homework(callback: CallbackQuery, state: FSMContext):
            await state.set_state(RegisterLesson.waiting_for_homework)
            await callback.message.edit_text(
                "<b>Пришлите скриншоты 📝 домашнего задания!\n\n</b>"
                "<b>Можно сразу несколько!</b>",
                parse_mode='HTML'
            )

        @self.router.message(RegisterLesson.waiting_for_homework, F.photo)
        async def process_homework_screenshots(message: Message, state: FSMContext, album: list[Message] = None):
            # 8. Обрабатываем скрины домашки
            # Определяем источник фото: список из альбома или одиночное сообщение
            media_to_process = album if album else [message]

            screenshots_to_add = []
            for msg in media_to_process:
                if msg.photo:
                    file_id = msg.photo[-1].file_id
                    screenshots_to_add.append({'file_id': file_id})

            if not screenshots_to_add:
                return await message.answer("❌ Не удалось распознать фото.")

            # Логика сохранения в FSM
            data = await state.get_data()
            existing = data.get('homework_screenshots', [])

            start_order = len(existing) + 1
            for i, scr in enumerate(screenshots_to_add, start=start_order):
                scr['order'] = i
                existing.append(scr)

            await state.update_data(homework_screenshots=existing)

            # Формируем ответ
            added_count = len(screenshots_to_add)
            total = len(existing)

            if added_count > 1:
                text = f"✅ Добавлено {added_count} скриншотов!\nВсего: {total}"
            else:
                text = f"✅ Скриншот {total} добавлен!"

            text += "\n\nМожете добавить ещё или нажмите 'Готово'"

            # Отвечаем на последнее сообщение (или единственное)
            await message.answer(
                text,
                reply_markup=await homework_from_lesson_create_done_keyboard()
            )


        @self.router.callback_query(F.data == 'finish_lesson')
        async def process_finish(callback: CallbackQuery, state: FSMContext):

            return await self._finish_create_lesson(callback, state)


        # ----------------------------------------------------------------
        # Прикрепление ДЗ
        # ----------------------------------------------------------------
        @self.router.callback_query(F.data == 'add_homework')
        async def process_add_homework(callback: CallbackQuery, state: FSMContext):
            # 1. Отображение всех lessons без homework
            teacher_tg_id = callback.from_user.id
            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)

            lessons = await self.lesson_service.repo.get_lessons_without_hw(teacher_id=teacher.id)

            for lesson in lessons:
                await callback.message.answer(
                    f"<b>id занятия 🔑: </b>{lesson.id}\n\n"
                    f"<b>Учитель 👨‍🏫:</b> {teacher.name} \n"
                    f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                    f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                    f"<b>Тема 📝: </b>{lesson.topics}\n"
                    f'<b>Дата 📅: </b>{lesson.created_at}\n',
                    parse_mode='HTML'
                )

            await callback.message.answer(
                f"<b>Отправьте id занятия 🔑, к которому хотите прикрепить ДЗ!</b>",
                parse_mode='HTML'
            )

            await state.set_state(RegisterHomework.choosing_lesson_id)

        @self.router.message(RegisterHomework.choosing_lesson_id)
        async def process_id_lesson(message: Message, state: FSMContext):
            # 2. Обработка конкретного lesson
            lesson_id = int(message.text)

            lesson = await self.lesson_service.repo.get_lesson_by_id(lesson_id)

            await state.update_data(lesson=lesson)

            await message.answer(
                f"<b>{lesson.teacher.name}, пришлите скриншоты 📝 домашнего задания!</b>\n\n"
                '<b>Можно сразу несколько!</b>',
                parse_mode='HTML'
            )

            await state.set_state(RegisterHomework.choosing_homework_screenshots)

        @self.router.message(RegisterHomework.choosing_homework_screenshots, F.photo)
        async def process_homework_screenshots(message: Message, state: FSMContext, album: list[Message] = None):
            # 3. Обработка скринов домашнего задания
            media_to_process = album if album else [message]

            screenshots_to_add = []
            for msg in media_to_process:
                if msg.photo:
                    file_id = msg.photo[-1].file_id
                    screenshots_to_add.append({'file_id': file_id})

            if not screenshots_to_add:
                return await message.answer("❌ Не удалось распознать фото.")

            # Логика сохранения в FSM
            data = await state.get_data()
            existing = data.get('homework_screenshots', [])

            start_order = len(existing) + 1
            for i, scr in enumerate(screenshots_to_add, start=start_order):
                scr['order'] = i
                existing.append(scr)

            await state.update_data(homework_screenshots=existing)

            # Формируем ответ
            added_count = len(screenshots_to_add)
            total = len(existing)

            if added_count > 1:
                text = f"✅ Добавлено {added_count} скриншотов!\nВсего: {total}"
            else:
                text = f"✅ Скриншот {total} добавлен!"

            text += "\n\nМожете добавить ещё или нажмите 'Готово'"

            # Отвечаем на последнее сообщение (или единственное)
            await message.answer(
                text,
                reply_markup=await homework_done_keyboard()
            )

        @self.router.callback_query(RegisterHomework.choosing_homework_screenshots, F.data == 'finish_homework')
        async def process_finish_homework(callback: CallbackQuery, state: FSMContext):
            await self._finish_create_homework(callback, state)


    async def _finish_create_homework(self, callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()

        lesson = data.get('lesson')
        teacher = lesson.teacher
        student = lesson.student
        subject = lesson.subject
        topics = lesson.topics
        homework_screenshots = data.get('homework_screenshots')

        homework = await self.homework_service.repo.create_homework(
            student_id = student.id,
            subject_id = subject.id,
            teacher_id = teacher.id,
            homework_screenshots = homework_screenshots,
            topics = topics
        )
        text = ''
        if homework:
            await self.lesson_service.repo.update_lesson_homework(
                lesson_id=lesson.id,
                homework_id=homework.id
            )
            text = (
                f'<b>Домашнее задание успешно добавлено! ✅</b>\n\n'
                f'<b>id занятия 🔑: </b>{lesson.id}\n'
                f"<b>Учитель 👨‍🏫:</b> {teacher.name} \n"
                f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                f"<b>Тема 📝: </b>{lesson.topics}\n"
                f'<b>Дата 📅: </b>{lesson.created_at}\n'
            )
        else:
            text = f'<b>Домашнее задание не было добавлено!</b>\n\n'

        await callback.message.answer(
            text,
            parse_mode='HTML'
        )

        await callback.message.answer(
            f'<b>{teacher.name}</b> 💬\n\nВыберите действие:\n\n',
            parse_mode='HTML',
            reply_markup=await teacher_inline()
        )

        await self.homework_service.notify_student_add_homework(
            student_tg_id = student.tg_id,
            teacher_name = teacher.name,
            subject_name = subject.name.value,
            lesson_id = lesson.id
        )

        await state.clear()


    async def _finish_create_lesson(self, callback, state):
        data = await state.get_data()

        teacher_id = data.get('teacher').id
        student_id = data.get('student').id
        subject_id = data.get('subject').id

        teacher = data.get('teacher')
        student = data.get('student')
        subject = data.get('subject')

        topics = data['topic']
        screenshots = data.get('screenshots')
        homework_screenshots = data.get('homework_screenshots')

        lesson = await self.lesson_service.repo.create_lesson(
            student_id = student_id,
            subject_id = subject_id,
            teacher_id = teacher_id,
            topics = topics,
            screenshots = screenshots
        )
        homework_success = ''
        if homework_screenshots:
            homework = await self.homework_service.repo.create_homework(
                student_id=student_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                topics=topics,
                homework_screenshots = homework_screenshots
            )

            await self.lesson_service.repo.update_lesson_homework(
                lesson_id = lesson.id,
                homework_id = homework.id
            )

            homework_success = '✅'
        else:
            homework_success = '❌'

        await callback.message.edit_text(
            "<b>Занятие успешно сформировано! ✅</b>\n\n"
            f"<b>Учитель 👨‍🏫:</b> {teacher.name} \n"
            f"<b>Ученик 👨‍🎓: </b>{student.name} \n"
            f"<b>Предмет 📚: </b>{subject.name.value} \n"
            f"<b>Конспект 📝: </b>✅\n"
            f"<b>ДЗ 📌: </b>{homework_success}\n\n"
            f'<b>Дата 📅: </b>{lesson.created_at}',
            parse_mode='HTML'
        )

        await callback.message.answer(
            f'<b>{teacher.name}</b> 💬\n\nВыберите действие:\n\n',
            parse_mode='HTML',
            reply_markup=await teacher_inline()
        )

        await self.lesson_service.notify_student_add_lesson(student_tg_id=student.tg_id, teacher_name=teacher.name, subject_name=subject.name.value)


        await state.clear()