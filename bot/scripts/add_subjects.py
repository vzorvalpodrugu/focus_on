import asyncio
from bot.models import Subject, SubjectEnum
from bot.database import async_session_maker

async def add_subjects():
    async with async_session_maker() as session:
        subjects = [
            Subject(name = SubjectEnum.PHYSICS),
            Subject(name = SubjectEnum.MATH)
        ]
        session.add_all(subjects)
        await session.commit()

if __name__ == '__main__':
    asyncio.run(add_subjects())