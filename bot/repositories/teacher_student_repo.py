from bot.repositories.base_repository import BaseRepository
from sqlalchemy import select
from bot.models import TeacherStudent, User

class TeacherStudentRepository(BaseRepository):

    async def get_students_by_teacher(self, teacher_id):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User)
                .join(TeacherStudent, User.id == TeacherStudent.student_id)
                .where(TeacherStudent.teacher_id == teacher_id)
            )

            return list(result.scalars().all())

    async def get_students_with_teacher_by_subject_id(self, subject_id : int):
        async with self.session_factory() as session:
            result = await session.execute(
                select(User)
                .join(TeacherStudent, TeacherStudent.student_id == User.id)
                .where(TeacherStudent.subject_id == subject_id)
            )

            return list(result.scalars().all())

    async def set_new_link(self, teacher_id : int, student_id : int, subject_id : int):
        async with self.session_factory() as session:
            teacher_student = TeacherStudent(
                teacher_id = teacher_id,
                student_id = student_id,
                subject_id = subject_id
            )

            session.add(teacher_student)

            await session.commit()