from sqlalchemy.orm import selectinload

from bot.repositories.base_repository import BaseRepository
from sqlalchemy import select, and_, or_
from bot.models import TeacherStudent, User, Subject


class TeacherStudentRepository(BaseRepository):

    async def get_teacher_student_subject_by_user_id(self, user_id):
        # Получить учитель-ученик-предмет по user_id
        async with self.session_factory() as session:
            result = await session.execute(
                select(TeacherStudent)
                .options(
                    selectinload(TeacherStudent.student),
                    selectinload(TeacherStudent.subject)
                )
                .where(TeacherStudent.teacher_id == user_id)
            )

            return list(result.scalars().all())

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


    async def get_user_subjects_by_teacher_id(self, student_id: int, teacher_id: int) -> list:
        # Получить предметы, по которым обучается студент у конкретного преподавателя
        async with self.session_factory() as session:
            data = await session.execute(
                select(Subject)
                .join(TeacherStudent, Subject.id == TeacherStudent.subject_id)
                .where(
                    and_(
                        TeacherStudent.student_id == student_id,
                        TeacherStudent.teacher_id == teacher_id,
                    )
                )
            )

            return list(data.scalars().all())


    async def set_new_link(self, teacher_id : int, student_id : int, subject_id : int):
        async with self.session_factory() as session:
            teacher_student = TeacherStudent(
                teacher_id = teacher_id,
                student_id = student_id,
                subject_id = subject_id
            )

            session.add(teacher_student)

            await session.commit()