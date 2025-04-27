#meta developer: @Python_Javs
from hikka import loader, utils
from telethon.tl.types import Message
import requests
import random

@loader.tds
class RandomCatMod(loader.Module):
    """Присылает случайных котиков и факты о них 😻"""
    strings = {
        "name": "RandomCat",
        "loading": "<b>😺 Ищу котика для тебя...</b>",
        "error": "<b>😿 Ой, что-то пошло не так!</b>",
    }

    async def client_ready(self, client, db):
        self._client = client

    @loader.command()
    async def кот(self, message: Message):
        """Прислать случайного котика"""
        await utils.answer(message, self.strings["loading"])
        
        try:
            # Получаем случайное фото кота
            cat_pic = requests.get("https://api.thecatapi.com/v1/images/search").json()[0]["url"]
            
            # Получаем случайный факт о котах (на русском)
            cat_fact = requests.get("https://catfact.ninja/fact").json()["fact"]
            
            # Собираем результат
            result = (
                f"<b>😻 Ваш котик дня!</b>\n\n"
                f"<i>📌 Факт:</i> {cat_fact}\n\n"
                f"<a href='{cat_pic}'>⠀</a>"
            )
            
            await self._client.send_file(
                message.peer_id,
                cat_pic,
                caption=result,
                reply_to=message.id
            )
            
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}\n<code>{e}</code>")

    @loader.command()
    async def котяра(self, message: Message):
        """Прислать особенного котика (с сюрпризом)"""
        await utils.answer(message, "<b>🐈 Ищу самого особенного котика...</b>")
        
        try:
            # Случайный выбор типа контента
            choice = random.randint(1, 3)
            
            if choice == 1:
                # GIF котика
                cat_gif = requests.get("https://api.thecatapi.com/v1/images/search?mime_types=gif").json()[0]["url"]
                await self._client.send_file(
                    message.peer_id,
                    cat_gif,
                    caption="<b>🎁 Вот тебе котик в движении!</b>",
                    reply_to=message.id
                )
                
            elif choice == 2:
                # Факт + фото
                await self.кот(message)
                
            else:
                # Случайная шутка про котов
                jokes = [
                    "Почему кот перешел дорогу? Потому что ему было плевать на ваши правила!",
                    "Как кот называет свой хвост? Сво-й хвост!",
                    "Кот — это единственное животное, которое может упасть с высоты и приземлиться на все четыре лапы... и на ваши нервы тоже!"
                ]
                await utils.answer(message, f"<b>😹 Кошачья шутка:</b>\n\n{random.choice(jokes)}")
                
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}\n<code>{e}</code>")