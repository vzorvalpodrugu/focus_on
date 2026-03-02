from aiogram.utils.keyboard import InlineKeyboardBuilder


async def choosing_period_keyboard(role: str):
    builder = InlineKeyboardBuilder()

    builder.button(text="📅 Последние 2 недели", callback_data="period_2weeks")
    builder.button(text="📆 Выбрать месяц", callback_data="period_month")
    builder.button(text="📚 Всё время", callback_data="period_all")

    if role == 'student':
        builder.button(text="◀️ Назад", callback_data="back_to_student_menu")
    elif role == 'teacher':
        builder.button(text="◀️ Назад", callback_data="back_to_teacher_menu")

    builder.adjust(1)

    return builder.as_markup()

async def choice_at_next_lesson_keyboard(role: str):
    builder = InlineKeyboardBuilder()


    builder.button(text='Другие уроки 🔍', callback_data='show_one_more_lesson')

    if role == 'student':
        builder.button(text="◀️ Назад", callback_data="back_to_student_menu")
    elif role == 'teacher':
        builder.button(text="◀️ Назад", callback_data="back_to_teacher_menu")

    builder.adjust(1)

    return builder.as_markup()