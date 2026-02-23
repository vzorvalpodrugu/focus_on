from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.models import DaysEnum
from bot.repositories.subject_repository import SubjectRepository
from bot.repositories.teacher_student_repo import TeacherStudentRepository
from bot.database import async_session_maker
from bot.repositories.user_repository import UserRepository


async def schedule_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text='➕ Добавить занятие', callback_data='add_schedule')
    builder.button(text='◀️ Назад', callback_data='back_to_teacher_menu')

    builder.adjust(1, 1)

    return builder.as_markup()

async def choosing_students_keyboard(teacher_id : int):
    builder = InlineKeyboardBuilder()
    teacher_student_repo = TeacherStudentRepository(async_session_maker)

    student_subject = await teacher_student_repo.get_teacher_student_subject_by_user_id(teacher_id)

    for ss in student_subject:

        student = ss.student
        subject = ss.subject

        builder.button(text=f'{student.name}\n{student.class_number} класс\nПредмет: {subject.name.value}', callback_data=f'stud_subj_id:{student.id}:{subject.id}')

    builder.adjust(1)

    return builder.as_markup()

async def choosing_day_keyboard():
    builder = InlineKeyboardBuilder()


    builder.button('flsfls', callback_data='fdf')

    return builder.as_markup()