from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def teacher_inline():
    builder = InlineKeyboardBuilder()

    builder.button(text='Мои ученики', callback_data='show_students')

    return builder.as_markup()


async def add_students():
    builder = InlineKeyboardBuilder()

    builder.button(text='➕ Добавить учеников', callback_data='add_students')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    return builder.as_markup()
