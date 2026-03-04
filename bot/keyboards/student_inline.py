from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def student_inline():
    builder = InlineKeyboardBuilder()

    builder.button(text='Профиль 👤', callback_data='show_profile')
    builder.button(text='Расписание 📅', callback_data='show_students_schedule')
    builder.button(text='Занятия 📖', callback_data='show_lessons')
    builder.button(text='Прикрепить ДЗ ➕', callback_data='add_done_homework')

    builder.adjust(1)

    return builder.as_markup()

async def back_to_student_menu():
    builder = InlineKeyboardBuilder()

    builder.button(text='◀️ Вернуться', callback_data='back_to_student_menu')

    builder.adjust(1)

    return builder.as_markup()

async def show_notify_lesson_student(lesson_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text='🔍 Посмотреть', callback_data=f'lesson_{lesson_id}')
    builder.button(text='◀️ Вернуться', callback_data='back_to_student_menu')

    builder.adjust(1)

    return builder.as_markup()