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