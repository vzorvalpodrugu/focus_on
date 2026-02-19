from bot.services.base_service import BaseService
from bot.models import User
from bot.repositories.user_repository import UserRepository

class UserService(BaseService):
    def __init__(self, user_repo, user_subject_repo):
        self.user_subject_repo = user_subject_repo
        super().__init__(user_repo)

    async def get_by_tg_id(self, tg_id: int) -> User:
        return await self.repo.get_by_tg_id(tg_id)

    async def register(self, tg_id: int, name: str, role: str, class_number: int = None, subject_ids: list[int] = None):
        exists = await self.repo.get_by_tg_id(tg_id)

        if exists:
            return {
                "success" : False,
                "message" : "Вы уже зарегистрированы!",
                'user' : None
            }
        else:

            new_user = await self.repo.create_user(
                tg_id=tg_id,
                name=name,
                role=role,
                class_number=class_number
            )

            print(role)
            if role == 'student' and subject_ids:
                print(new_user.id)
                await self.user_subject_repo.add_subjects_to_student(new_user.id, subject_ids)

            return {
                "success": True,
                "message": "✅ Вы успешно зарегистрированы!",
                "user" : new_user
            }