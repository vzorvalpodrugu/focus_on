from bot.repositories.base_repository import BaseRepository
from sqlalchemy import select
from bot.models import Subject

class SubjectRepository(BaseRepository):

    async def get_subjects(self):
        async with self.session_factory() as session:
            result = await session.execute(select(Subject))

            return list(result.scalars().all())
