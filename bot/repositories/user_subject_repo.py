from bot.repositories.base_repository import BaseRepository
from sqlalchemy import select, and_
from bot.models import UserSubject
from typing import List

class UserSubjectRepository(BaseRepository):

    async def add_subject_to_student(self, student_id, subject_id):
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
        async with self.session_factory() as session:
            for subj_id in subject_ids:
                await self.add_subject_to_student(student_id, subj_id)

    async def get_user_subjects(self, student_id) -> list:
        async with self.session_factory() as session:
            data = await session.execute(
                select(UserSubject).where(UserSubject.user_id == student_id)
            )

            return list(data.scalars().all())