import asyncio
from typing import Any, Dict, List, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.1):
        self.latency = latency
        self.cache: Dict[str, List[Message]] = {}

    async def __call__(
            self,
            handler,
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        # Если это не часть альбома, просто прокидываем дальше
        if not event.media_group_id:
            return await handler(event, data)

        # Если это первое сообщение из группы
        if event.media_group_id not in self.cache:
            self.cache[event.media_group_id] = [event]

            # Ждем короткое время, пока придут остальные части
            await asyncio.sleep(self.latency)

            # Достаем все собранные сообщения и передаем в хендлер
            data["album"] = self.cache.pop(event.media_group_id)
            return await handler(event, data)

        # Если это последующее сообщение группы, просто добавляем в кэш и «тушим»
        else:
            self.cache[event.media_group_id].append(event)
            return None
