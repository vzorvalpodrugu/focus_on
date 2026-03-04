from aiogram.utils.keyboard import InlineKeyboardBuilder



async def teacher_inline():
    builder = InlineKeyboardBuilder()

    builder.button(text='Мои ученики 👨‍🎓', callback_data='show_students')
    builder.button(text='Расписание 📅', callback_data='show_schedules')
    builder.button(text='Новый урок 📄', callback_data='create_lesson')
    builder.button(text='Прикрепить ДЗ ➕', callback_data='add_homework')
    builder.button(text='Занятия 📖', callback_data='show_lessons')

    builder.adjust(1, 1)

    return builder.as_markup()

async def back_to_teacher_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='◀️ Вернуться', callback_data='back_to_teacher_menu')

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


async def show_notify_lesson_teacher(lesson_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text='🔍 Посмотреть', callback_data=f'lesson_{lesson_id}')
    builder.button(text='◀️ Вернуться', callback_data='back_to_student_menu')

    builder.adjust(1)

    return builder.as_markup()