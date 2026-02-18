from bot.services.base_service import BaseService
from bot.models import User
from bot.repositories.user_repository import UserRepository

class UserService(BaseService):
    def __init__(self, repo):
        super().__init__(repo)

    async def get_by_tg_id(self, tg_id: int) -> User:
        return await self.repo.get_by_tg_id(tg_id)

    async def register(self, tg_id: int, name: str, role: str, class_number: int = None):
        exists = await self.repo.get_by_tg_id(tg_id)

        if exists:
            return {
                "success" : False,
                "message" : "Вы уже зарегистрированы!"
            }
        else:
            await self.repo.create_user(
                tg_id=tg_id,
                name=name,
                role=role,
                class_number=class_number
            )

            return {
                "success": True,
                "message": "✅ Вы успешно зарегистрированы!"
            }