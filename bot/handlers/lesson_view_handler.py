from typing import Coroutine

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InlineKeyboardMarkup
from aiogram import F, Bot

from bot.handlers.base_handler import BaseHandler
from bot.keyboards.lesson_view_inline import choosing_period_keyboard, choice_at_next_lesson_keyboard, \
    choose_month_keyboard, back_to_menu_keyboard
from bot.keyboards.student_inline import back_to_student_menu, student_homework_keyboard
from bot.config import TG_TOKEN
from bot.keyboards.teacher_inline import students_without_done_hw_keyboard, back_to_teacher_menu_keyboard, \
    lessons_without_done_homework, teacher_view_one_more_lesson
from bot.states.lesson_view_states import LessonViewStates
from bot.states.register_done_homework import RegisterDoneHomework
from bot.states.view_students_without_done_hw_state import ViewStudentsWithoutDoneHw


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
            # 2.1. Обработка периода
            period = callback.data.replace('period_', '')

            data = await state.get_data()
            user = data.get('user')

            lessons = await self.lesson_service.repo.get_lessons_by_period(user_id=user.id, role=user.role, period_type=period)

            lessons_id = []

            for lesson in lessons:
                lessons_id.append(lesson.id)
                await callback.message.answer(
                    f"<b>id занятия 🔑: </b>{lesson.id}\n\n"
                    f"<b>Учитель 👨‍🏫:</b> {lesson.teacher.name} \n"
                    f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                    f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                    f"<b>Тема 📝: </b>{lesson.topics}\n"
                    f"<b>Количество вып-ых заданий 🏆:</b> {lesson.quantity_tasks}\n\n"
                    f'<b>Дата 📅: </b>{lesson.created_at}',
                    parse_mode='HTML'
                )

                await state.update_data(lessons_id=lessons_id)

            await callback.message.answer(
                f"<b>Отправьте id занятия 🔑, которое хотели бы посмотреть!</b>",
                parse_mode='HTML',
                reply_markup=await back_to_menu_keyboard(role=user.role)
            )

            await state.set_state(LessonViewStates.choosing_lesson_id)

        @self.router.callback_query(LessonViewStates.choosing_period, F.data.startswith('choose_month'))
        async def process_choose_month(callback: CallbackQuery, state: FSMContext):
            # 2.2 Выбор месяца
            data = await state.get_data()
            user = data.get('user')

            await callback.message.answer(
                f'<b>Выберите месяц 📆, в котором хотите просмотреть занятия!</b>',
                parse_mode = 'HTML',
                reply_markup=await choose_month_keyboard(role=user.role)
            )

        @self.router.callback_query(LessonViewStates.choosing_period, F.data.startswith('month_'))
        async def process_month(callback: CallbackQuery, state: FSMContext):
            # 2.2 Обработка месяца
            period = callback.data.replace('month_', '')

            data = await state.get_data()
            user = data.get('user')

            lessons = await self.lesson_service.repo.get_lessons_by_period(user_id=user.id, role=user.role,
                                                                           period_type=period)
            lessons_id = []

            if lessons:
                for lesson in lessons:
                    lessons_id.append(lesson.id)
                    await callback.message.answer(
                        f"<b>id занятия 🔑: </b>{lesson.id}\n\n"
                        f"<b>Учитель 👨‍🏫:</b> {lesson.teacher.name} \n"
                        f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                        f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                        f"<b>Тема 📝: </b>{lesson.topics}\n"
                        f"<b>Количество вып-ых заданий 🏆:</b> {lesson.quantity_tasks}\n\n"
                        f'<b>Дата 📅: </b>{lesson.created_at}',
                        parse_mode='HTML'
                    )

                await state.update_data(lessons_id=lessons_id)

                await callback.message.answer(
                    f"<b>Отправьте id занятия 🔑, которое хотели бы посмотреть!</b>",
                    parse_mode='HTML',
                    reply_markup=await back_to_menu_keyboard(role=user.role)
                )

                await state.set_state(LessonViewStates.choosing_lesson_id)
            else:
                await callback.message.edit_text(
                    f'<b>В этом месяце, у вас не было занятий.</b>\n\n'
                    f'<b>Попробуйте выбрать другой месяц или поменяйте период :)</b>',
                    parse_mode='HTML',
                    reply_markup=await choosing_period_keyboard(role=user.role)
                )

        @self.router.message(LessonViewStates.choosing_lesson_id)
        async def process_lesson_id(message: Message, state: FSMContext):
            # 3. Отображение урока
            lesson_id = int(message.text)
            user = (await state.get_data()).get('user')

            lessons_id = (await state.get_data()).get('lessons_id')
            if lesson_id not in lessons_id:
                await message.answer(
                    f'<b>Вы не можете просмотреть данный урок.</b>\n\n'
                    f'<b>Попробуйте ещё раз :)</b>',
                    parse_mode='HTML'
                )
                return

            bot = Bot(token=TG_TOKEN)


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

            if lesson.done_homework:

                done_homework_media_group = [
                    InputMediaPhoto(media=screenshot.file_id)
                    for screenshot in lesson.done_homework.done_homework_screenshots
                ]

                await message.answer(
                    f'<b>Выполненное домашнее задание 📓:</b>',
                    parse_mode='HTML'
                )

                if done_homework_media_group:
                    await bot.send_media_group(
                        chat_id=message.chat.id,
                        media=done_homework_media_group
                    )


            await message.answer(
                text = '<b>Выберите действие 💬:</b>',
                parse_mode='HTML',
                reply_markup=await choice_at_next_lesson_keyboard(role=user.role)
            )

        @self.router.callback_query(F.data == 'show_one_more_lesson')
        async def process_one_more_lesson(callback: CallbackQuery, state: FSMContext):
            user = (await state.get_data()).get('user')

            await state.set_state(LessonViewStates.choosing_lesson_id)
            await callback.message.edit_text(
                f"<b>Отправьте id занятия 🔑, которое хотели бы посмотреть!</b>",
                parse_mode='HTML',
                reply_markup=await back_to_menu_keyboard(role=user.role)
            )

        @self.router.callback_query(F.data.startswith('lesson_'))
        async def process_lesson_id(callback: CallbackQuery, state: FSMContext):
            # Функция для отображения урока из оповещения по колбеку
            user_id = callback.from_user.id

            user = await self.user_service.get_by_tg_id(user_id)

            lesson_id = int(callback.data.replace('lesson_', ''))

            bot = Bot(token=TG_TOKEN)

            lesson = await self.lesson_service.repo.get_lesson_by_id(lesson_id=lesson_id)

            lesson_media_group = [
                InputMediaPhoto(media=screenshot.file_id)
                for screenshot in lesson.lesson_screenshots
            ]
            await callback.message.answer(
                f'<b>Конспект 📝:</b>',
                parse_mode='HTML'
            )
            if lesson_media_group:
                await bot.send_media_group(
                    chat_id=callback.message.chat.id,
                    media=lesson_media_group
                )

            if lesson.homework:

                homework_media_group = [
                    InputMediaPhoto(media=screenshot.file_id)
                    for screenshot in lesson.homework.homework_screenshots
                ]

                await callback.message.answer(
                    f'<b>Домашнее задание 📓:</b>',
                    parse_mode='HTML'
                )

                if homework_media_group:
                    await bot.send_media_group(
                        chat_id=callback.message.chat.id,
                        media=homework_media_group
                    )

            if lesson.done_homework:

                done_homework_media_group = [
                    InputMediaPhoto(media=screenshot.file_id)
                    for screenshot in lesson.done_homework.done_homework_screenshots
                ]

                await callback.message.answer(
                    f'<b>Выполненное домашнее задание 📓:</b>',
                    parse_mode='HTML'
                )

                if done_homework_media_group:
                    await bot.send_media_group(
                        chat_id=callback.message.chat.id,
                        media=done_homework_media_group
                    )

            kb = InlineKeyboardMarkup

            if user.role == 'teacher':
                kb = await teacher_view_one_more_lesson(lesson.student_id)
                await state.set_state(ViewStudentsWithoutDoneHw.choosing_student)
            elif user.role == 'student':
                kb = await back_to_menu_keyboard(role=user.role)

            await callback.message.answer(
                text = f'<b>Выберите действие 💬:</b>',
                parse_mode='HTML',
                reply_markup=kb
            )



        @self.router.callback_query(F.data == 'show_homeworks')
        async def process_show_homeworks(callback: CallbackQuery, state: FSMContext):
            # Показать все невыполненные домашки ученика
            user_tg_id = callback.from_user.id

            user = await self.user_service.repo.get_by_tg_id(user_tg_id)

            await state.update_data(user=user)

            lessons = await self.lesson_service.repo.get_lessons_without_done_hw(user_id=user.id)
            lessons_id = []

            if lessons:
                for lesson in lessons:
                    lessons_id.append(lesson.id)
                    await callback.message.answer(
                        f"<b>id занятия 🔑: </b>{lesson.id}\n\n"
                        f"<b>Учитель 👨‍🏫:</b> {lesson.teacher.name} \n"
                        f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                        f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                        f"<b>Тема 📝: </b>{lesson.topics}\n"
                        f"<b>Количество вып-ых заданий 🏆:</b> {lesson.quantity_tasks}\n\n"
                        f'<b>Дата 📅: </b>{lesson.created_at}',
                        parse_mode='HTML'
                    )

                await callback.message.answer(
                    f"<b>По вышеуказанным занятиям требуется выполнить ДЗ 📓.</b>\n\n"
                    f'<b>Выберите действие: </b>',
                    parse_mode='HTML',
                    reply_markup=await student_homework_keyboard(lessons)
                )

                await state.set_state(RegisterDoneHomework.choosing_lesson_id)
                await state.update_data(lessons_id=lessons_id)

            else:
                await callback.message.edit_text(
                    f'<b>У вас выполнены все ДЗ. Отдыхайте и радуйтесь жизни :D</b>\n\n',
                    parse_mode='HTML',
                    reply_markup=await back_to_menu_keyboard(role=user.role)
                )


        @self.router.callback_query(F.data == 'show_students_without_done_hw')
        async def process_students(callback: CallbackQuery, state: FSMContext):
            # 1. Отображение учеников без выполненного ДЗ
            teacher_tg_id = callback.from_user.id

            teacher = await self.user_service.get_by_tg_id(teacher_tg_id)

            lessons = await self.lesson_service.repo.get_lessons_without_done_hw(user_id=teacher.id)

            await state.update_data(lessons = lessons)

            if lessons:
                students_all = [lesson.student for lesson in lessons]

                unique_students_id = []
                students = []

                for student in students_all:
                    if student.id not in unique_students_id:
                        unique_students_id.append(student.id)
                        students.append(student)

                await callback.message.edit_text(
                    f'<b>Выберите ученика 👨‍🎓, у которого нет выполненного ДЗ 📓</b>\n\n'
                    f'<b>Обратите внимание, что в списке только ученики с долгами⚠️</b>',
                    parse_mode='HTML',
                    reply_markup=await students_without_done_hw_keyboard(students)
                )

                await state.set_state(ViewStudentsWithoutDoneHw.choosing_student)

            else:
                await callback.message.edit_text(
                    f'<b>Все ученики 👨‍🎓 уже выполнили свои ДЗ 📓!</b>',
                    parse_mode='HTML',
                    reply_markup=await back_to_teacher_menu_keyboard()
                )

        @self.router.callback_query(ViewStudentsWithoutDoneHw.choosing_student, F.data.startswith('student_'))
        async def process_student_id(callback: CallbackQuery, state: FSMContext):
            # 2. Отображение уроков с невыполненными ДЗ ученика со student_id
            student_id = int(callback.data.replace('student_', ''))
            lessons_all = (await state.get_data()).get('lessons')

            lessons = [lesson for lesson in lessons_all if lesson.student.id == student_id]

            lessons_id = []
            for lesson in lessons:
                lessons_id.append(lesson.id)
                await callback.message.answer(
                    f"<b>id занятия 🔑: </b>{lesson.id}\n\n"
                    f"<b>Учитель 👨‍🏫:</b> {lesson.teacher.name} \n"
                    f"<b>Ученик 👨‍🎓: </b>{lesson.student.name} \n"
                    f"<b>Предмет 📚: </b>{lesson.subject.name.value} \n"
                    f"<b>Тема 📝: </b>{lesson.topics}\n"
                    f"<b>Количество вып-ых заданий 🏆:</b> {lesson.quantity_tasks}\n\n"
                    f'<b>Дата 📅: </b>{lesson.created_at}',
                    parse_mode='HTML'
                )

            await callback.message.answer(
                f"<b>Выберите нужное занятие 🔑: </b>\n\n"
                f"<b>Обратите внимание, что в списке только те занятия 🔑, где долг ⚠️ по ДЗ!</b>",
                parse_mode='HTML',
                reply_markup=await lessons_without_done_homework(lessons_id)
            )

            await state.set_state(ViewStudentsWithoutDoneHw.choosing_lesson)















