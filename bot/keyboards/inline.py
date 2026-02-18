from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def role_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора роли"""
    builder = InlineKeyboardBuilder()
    builder.button(text='👨‍🎓 Ученик', callback_data='role_student')
    builder.button(text='👨‍🏫 Учитель', callback_data='role_teacher')
    builder.adjust(1)

    return builder.as_markup()

def class_number_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора класса для ученика"""
    builder = InlineKeyboardBuilder()
    for i in range(5, 12):
        builder.button(text=f'{i} класс', callback_data=f'class_{i}')

    builder.button(text='◀️ Назад', callback_data='back_to_start')

    builder.adjust(3, 3, 1, 1)

    return builder.as_markup()

def back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()
    builder.button(text='◀️ Назад', callback_data='back_to_start')

    return builder.as_markup()