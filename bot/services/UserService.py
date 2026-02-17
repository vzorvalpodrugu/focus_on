from bot.services.BaseService import BaseSevice
from bot.models import User
from bot.repositories.UserRepository import UserRepository

class UserService(BaseSevice):

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
            new_user = await self.repo.create_user(
                tg_id=tg_id,
                name=name,
                role=role,
                class_number=class_number
            )

            return {
                "success": True,
                "message": "Вы успешно зарегистрированы!"
            }