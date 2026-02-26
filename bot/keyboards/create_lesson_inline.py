from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.repositories.teacher_student_repo import TeacherStudentRepository
from bot.database import async_session_maker

async def choosing_student_keyboard(teacher_id: int):
    teacher_student_repo = TeacherStudentRepository(async_session_maker)
    students = await teacher_student_repo.get_unique_students_by_teacher(teacher_id)

    builder = InlineKeyboardBuilder()

    for student in students:
        builder.button(text=f'{student.name}, {student.class_number} класс', callback_data=f'student_{student.id}')

    builder.button(text='◀️ Вернуться', callback_data='back_to_teacher_menu')
    builder.adjust(1)

    return builder.as_markup()

async def choosing_subject_keyboard(teacher_id: int, student_id: int):
    teacher_student_repo = TeacherStudentRepository(async_session_maker)
    subjects = await teacher_student_repo.get_user_subjects_by_teacher_id(student_id, teacher_id)

    builder = InlineKeyboardBuilder()

    for subject in subjects:
        builder.button(text=f'{subject.name.value}', callback_data=f'subject_{subject.id}')

    builder.button(text='◀️ Вернуться', callback_data='back_to_teacher_menu')

    builder.adjust(1)

    return  builder.as_markup()

async def screenshots_done_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='Готово', callback_data = 'create_homework')
    builder.button(text='◀️ Вернуться', callback_data='back_to_teacher_menu')

    builder.adjust(1)

    return builder.as_markup()

async def homework_done_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='Готово', callback_data='finish_lesson')
    builder.button(text='◀️ Вернуться', callback_data='back_to_teacher_menu')

    builder.adjust(1)

    return builder.as_markup()



