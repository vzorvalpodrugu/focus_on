from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.repositories.subject_repository import SubjectRepository
from bot.database import async_session_maker

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

async def subjects_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    subj_repo = SubjectRepository(async_session_maker)
    subjects = await subj_repo.get_subjects()

    for i in range (1, len(subjects)+1):
        builder.button(text=f'{str(subjects[i-1].name.value)}', callback_data=f'sub_{i}')

    builder.adjust(1)

    return builder.as_markup()




def back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()
    builder.button(text='◀️ Назад', callback_data='back_to_start')

    return builder.as_markup()