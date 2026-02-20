from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.repositories.subject_repository import SubjectRepository
from bot.database import async_session_maker
from bot.services.user_service import UserService


async def teacher_inline():
    builder = InlineKeyboardBuilder()

    builder.button(text='Мои ученики', callback_data='show_students')

    return builder.as_markup()


async def add_students():
    builder = InlineKeyboardBuilder()

    builder.button(text='➕ Добавить учеников', callback_data='show_subjects')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    return builder.as_markup()

async def subjects_keyboard(subjects):
    builder = InlineKeyboardBuilder()
    print(subjects)
    for subject in subjects:
        builder.button(
            text=f"{subject.name.value}",
            callback_data=f"choose_student_with_subject_{subject.id}"
        )

    builder.button(text="◀️ Назад", callback_data="back_to_teacher_menu")

    builder.adjust(2, 1)

    return builder.as_markup()

async def student_by_subject_keyboard(students):
    builder = InlineKeyboardBuilder()

    for student in students:
        builder.button(
            text=f"{student.name} : {student.class_number} класс",
            callback_data=f"student_{student.id}"
        )

    builder.button(text="◀️ Назад", callback_data="back_to_teacher_menu")

    builder.adjust(1)

    return builder.as_markup()