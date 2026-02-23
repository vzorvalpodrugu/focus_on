from bot.repositories.base_repository import BaseRepository
from sqlalchemy import select, and_
from bot.models import UserSubject, Subject, User
from typing import List

class UserSubjectRepository(BaseRepository):

    async def add_subject_to_student(self, student_id, subject_id):
        # Добавить предмет студенту
        async with self.session_factory() as session:
            exists = await session.execute(
                select(UserSubject).where(
                    and_(
                        UserSubject.user_id == student_id,
                        UserSubject.subject_id == subject_id
                    )
                )
            )

            if not exists.scalar_one_or_none():
                user_subject = UserSubject(
                    user_id = student_id,
                    subject_id = subject_id
                )

                session.add(user_subject)
                await session.commit()

    async def add_subjects_to_student(self, student_id : int, subject_ids : list[int]):
        # Добавить предметы студенту
        async with self.session_factory() as session:
            for subj_id in subject_ids:
                await self.add_subject_to_student(student_id, subj_id)

    async def get_user_subjects(self, user_id : int) -> list:
        # Получить предметы, по которым обучается студент
        async with self.session_factory() as session:
            data = await session.execute(
                select(Subject)
                .join(UserSubject, Subject.id == UserSubject.subject_id)
                .where(UserSubject.user_id == user_id)
            )

            return list(data.scalars().all())


    async def get_users_by_subject_id(self, subject_id : int):
        # Получить студентов, которые обучаются данному по предмету
        async with self.session_factory() as session:
            result = await session.execute(
                select(User)
                .join(UserSubject, UserSubject.user_id == User.id)
                .where(
                    and_(
                        UserSubject.subject_id == subject_id,
                        User.role == 'student'
                    )
                )
            )

            return list(result.scalars().all())

