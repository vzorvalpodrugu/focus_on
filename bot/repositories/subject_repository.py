from bot.repositories.base_repository import BaseRepository
from sqlalchemy import select
from bot.models import Subject

class SubjectRepository(BaseRepository):

    async def get_subjects(self):
        async with self.session_factory() as session:
            result = await session.execute(select(Subject))

            return list(result.scalars().all())


    async def get_subject_by_id(self, subject_id: int):
        async with self.session_factory() as session:
            result = await session.execute(
                select(Subject)
                .where(Subject.id == subject_id)
            )

            return result.scalar_one_or_none()

    async def get_by_ids(self, subj_ids) -> list:
        async with self.session_factory() as session:
            result = await session.execute(select(Subject).where(Subject.id.in_(subj_ids)))

            return list(result.scalars().all())