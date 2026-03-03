from aiogram.utils.keyboard import InlineKeyboardBuilder


async def choosing_period_keyboard(role: str):
    builder = InlineKeyboardBuilder()

    builder.button(text="📅 Последние 2 недели", callback_data="period_2weeks")
    builder.button(text="📆 Выбрать месяц", callback_data="choose_month")
    builder.button(text="📚 Всё время", callback_data="period_all")
    builder.button(text='⏳ Последнее', callback_data='period_last')
    builder.button(text='🔑 По id занятия', callback_data = 'show_one_more_lesson')

    if role == 'student':
        builder.button(text="◀️ Назад", callback_data="back_to_student_menu")
    elif role == 'teacher':
        builder.button(text="◀️ Назад", callback_data="back_to_teacher_menu")

    builder.adjust(1)

    return builder.as_markup()

async def choose_month_keyboard(role: str):
    builder = InlineKeyboardBuilder()

    builder.button(text='Январь ❄️', callback_data='month_1')
    builder.button(text='Февраль ❄️', callback_data='month_2')
    builder.button(text='Март 🌷', callback_data='month_3')
    builder.button(text='Апрель 🌷', callback_data='month_4')
    builder.button(text='Май 🌷', callback_data='month_5')
    builder.button(text='Июнь 🔥', callback_data='month_6')
    builder.button(text='Июль 🔥', callback_data='month_7')
    builder.button(text='Август 🔥', callback_data='month_8')
    builder.button(text='Сентябрь 🍁', callback_data='month_9')
    builder.button(text='Октябрь 🍁', callback_data='month_10')
    builder.button(text='Ноябрь 🍁', callback_data='month_11')
    builder.button(text='Декабрь ❄️', callback_data='month_12')

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

async def back_to_menu_keyboard(role: str):
    builder = InlineKeyboardBuilder()

    if role == 'student':
        builder.button(text="◀️ Назад", callback_data="back_to_student_menu")
    elif role == 'teacher':
        builder.button(text="◀️ Назад", callback_data="back_to_teacher_menu")

    builder.adjust(1)
    return builder.as_markup()