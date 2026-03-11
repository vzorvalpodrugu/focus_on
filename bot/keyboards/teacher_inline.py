from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.models import User, Lesson


async def teacher_inline():
    builder = InlineKeyboardBuilder()

    builder.button(text='Мои ученики 👨‍🎓', callback_data='show_students')
    builder.button(text='Расписание 📅', callback_data='show_schedules')
    builder.button(text='Новый урок 📄', callback_data='create_lesson')
    builder.button(text='Домашние задания 📓', callback_data='show_homeworks_for_teacher')
    builder.button(text='Занятия 📖', callback_data='show_lessons')

    builder.adjust(1, 1)

    return builder.as_markup()

async def teacher_homeworks_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='Ученики без ДЗ 📓', callback_data='show_students_without_hw')
    builder.button(text='Ученики без выполненного ДЗ 📓⚠️', callback_data='show_students_without_done_hw')
    builder.button(text='Непроверенные ДЗ 📓⚠️', callback_data = 'show_lessons_without_marked_hw')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()

async def students_without_done_hw_keyboard(students: list[User]):
    builder = InlineKeyboardBuilder()

    for student in students:
        builder.button(text=f'{student.name} 👨‍🎓 / {student.class_number} класс 🎓', callback_data=f'student_{student.id}')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()

async def lessons_without_done_homework(lessons_id: list[int]):
    builder = InlineKeyboardBuilder()

    for lesson_id in lessons_id:
        builder.button(text=f'Занятие {lesson_id} 🔑', callback_data=f'lesson_{lesson_id}')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()


async def teacher_view_one_more_lesson(student_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text='Выбрать другое занятие 🔑', callback_data=f'student_{student_id}')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()


async def teacher_lessons_without_hw(lessons: list[Lesson]):
    builder = InlineKeyboardBuilder()

    for lesson in lessons:
        builder.button(text=f'Занятие {lesson.id} 🔑', callback_data=f'lesson_{lesson.id}')

    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()


async def choose_mark_or_another_lesson_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='Поставить оценку ➕', callback_data='add_mark')
    builder.button(text='Выбрать другое занятие 🔑', callback_data='show_lessons_without_marked_hw')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)


    return builder.as_markup()


async def choose_mark_keyboard():
    builder = InlineKeyboardBuilder()

    for i in range(0, 11):
        postfix = ''

        if i < 4:
            postfix = '❌'
        elif (i >= 4) and i < 7:
            postfix = '😐'
        elif (i >= 7) and i < 9:
            postfix = '👍'
        elif (i >= 9) and i < 11:
            postfix = '🏆'

        builder.button(text = f'{i} {postfix}', callback_data=f'mark_{i}')

    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()


async def teacher_done_homework_keyboard(student_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text='Прикрепить ДЗ ➕', callback_data='add_homework')
    builder.button(text='Выбрать другое занятие 🔑', callback_data=f'show_homeworks_student_{student_id}')
    builder.button(text='◀️ Вернуться', callback_data='back_to_teacher_menu')

    builder.adjust(1)

    return builder.as_markup()


async def choose_students_without_hw(students: list[User]):
    builder = InlineKeyboardBuilder()

    for student in students:
        builder.button(text=f'{student.name} 👨‍🎓 / {student.class_number} класс 🎓', callback_data=f'student_{student.id}')

    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

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