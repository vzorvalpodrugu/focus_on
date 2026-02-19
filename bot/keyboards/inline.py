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

async def subjects_keyboard(selected_ids: list[int] = None) -> InlineKeyboardMarkup:
    """
    selected_ids - список ID уже выбранных предметов
    """
    builder = InlineKeyboardBuilder()

    subj_repo = SubjectRepository(async_session_maker)
    subjects = await subj_repo.get_subjects()
    selected_ids = selected_ids or []

    for subject in subjects:
        # Ставим галочку, если предмет уже выбран
        prefix = "✅ " if subject.id in selected_ids else ""
        builder.button(
            text=f"{prefix}{subject.name.value}",
            callback_data=f"subject_{subject.id}"
        )

    # Кнопки управления
    builder.button(text="✅ Готово", callback_data="subjects_done")
    builder.button(text="◀️ Назад", callback_data="back_to_start")

    # Расположение: предметы по 2 в ряд, потом кнопки управления
    builder.adjust(2, 2, 1, 1)  # можно настроить под себя
    return builder.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    builder = InlineKeyboardBuilder()
    builder.button(text='◀️ Назад', callback_data='back_to_start')

    return builder.as_markup()