import asyncio
from bot.database import async_session_maker
from bot.repositories.base_repository import BaseRepository
from bot.models import User
from sqlalchemy import select

class UserRepository(BaseRepository):

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.tg_id==tg_id))

            return result.scalar_one_or_none()


    async def get_teachers(self):
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.role=='teacher'))

            return list(result.scalars().all())

    async def get_students(self):
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.role == 'student'))

            return list(result.scalars().all())

    async def create_user(self,tg_id, name, role, class_number = None):
        async with self.session_factory() as session:
            user = User(
                tg_id=tg_id,
                name=name,
                class_number=class_number,
                role=role
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            return user

async def main():
    repo = UserRepository(session_factory=async_session_maker)

    res = await repo.create_user(tg_id=12434, name="Angel", role='teacher')

if __name__ == '__main__':
    asyncio.run(main())