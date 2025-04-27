#meta developer: @Python_Javs
from hikka import loader, utils
from telethon.tl.types import Message
import requests
import random
import asyncio
from datetime import datetime

@loader.tds
class UltimateAnimeMod(loader.Module):
    """🔥 Ultimate аниме-модуль с API интеграцией"""
    strings = {
        "name": "AnimeUltimate",
        "loading": "<b>🌀 Загружаю аниме-данные...</b>",
        "error": "<b>💢 Ошибка! Проверьте название или попробуйте позже</b>",
        "no_args": "<b>🔍 Укажите запрос (например: .anime Наруто)</b>",
    }

    async def client_ready(self, client, db):
        self._client = client
        self.db = db
        self.jikan_url = "https://api.jikan.moe/v4"
        self.waifu_pics = "https://api.waifu.pics"

    # Основные команды
    @loader.command()
    async def anime(self, message: Message):
        """Найти аниме по названию"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"])
            return
        
        await utils.answer(message, self.strings["loading"])
        
        try:
            data = await self._get_anime_data(args)
            if not data:
                await utils.answer(message, f"{self.strings['error']}: Аниме не найдено")
                return
            
            text = (
                f"🎬 <b>{data['title']}</b>\n\n"
                f"⭐ <b>Рейтинг:</b> {data['score']}/10\n"
                f"📅 <b>Год:</b> {data['year']}\n"
                f"📺 <b>Эпизоды:</b> {data['episodes']}\n"
                f"🌀 <b>Статус:</b> {data['status']}\n\n"
                f"📝 <b>Описание:</b>\n{data['synopsis'][:300]}..."
            )
            
            if data['image_url']:
                await self._client.send_file(
                    message.peer_id,
                    data['image_url'],
                    caption=text,
                    reply_to=message.id
                )
            else:
                await utils.answer(message, text)
                
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}\n<code>{e}</code>")

    @loader.command()
    async def waifu(self, message: Message):
        """Случайная вайфу (NSFW/SFW)"""
        await utils.answer(message, self.strings["loading"])
        try:
            category = random.choice(["sfw", "nsfw"])
            types = ["waifu", "neko", "awoo"] if category == "sfw" else ["waifu", "neko"]
            img_url = requests.post(
                f"{self.waifu_pics}/many/{category}/{random.choice(types)}",
                json={"exclude": []}
            ).json()["files"][0]
            
            await self._client.send_file(
                message.peer_id,
                img_url,
                caption=f"💖 <b>Ваша вайфу</b> ({category.upper()})",
                reply_to=message.id
            )
        except Exception as e:
            await utils.answer(message, f"{self.strings['error']}\n<code>{e}</code>")

    # Дополнительные функции
    @loader.command()
    async def animerel(self, message: Message):
        """Калькулятор отношений"""
        args = utils.get_args_raw(message)
        name = args if args else "Ты"
        score = random.randint(30, 100)
        
        result = (
            f"💞 <b>Калькулятор отношений:</b>\n\n"
            f"❤ {name} и {random.choice(['Сакура', 'Зеро Ту', 'Рем', 'Мику'])} - {score}%\n"
            f"🔥 Химия: {random.randint(50, 100)}%\n"
            f"💍 Шанс брака: {random.randint(10, 80)}%\n\n"
            f"📌 <i>Совет:</i> {random.choice(['Дарите больше подарков!', 'Совместный просмотр аниме сближает!'])}"
        )
        await utils.answer(message, result)

    @loader.command()
    async def animegen(self, message: Message):
        """Рекомендация по жанру"""
        genres = ["Сёнен", "Романтика", "Фэнтези", "Меха", "Хоррор"]
        chosen = random.choice(genres)
        
        recs = {
            "Сёнен": ["Attack on Titan", "Naruto", "One Piece"],
            "Романтика": ["Your Lie in April", "Toradora!", "Clannad"],
            "Фэнтези": ["Re:Zero", "Sword Art Online", "No Game No Life"],
            "Меха": ["Code Geass", "Gundam", "Neon Genesis Evangelion"],
            "Хоррор": ["Another", "Higurashi", "Tokyo Ghoul"]
        }
        
        text = (
            f"🎌 <b>Рекомендации ({chosen}):</b>\n\n"
            f"1. {recs[chosen][0]}\n"
            f"2. {recs[chosen][1]}\n"
            f"3. {recs[chosen][2]}\n\n"
            f"💡 Используй <code>.anime Название</code> для поиска"
        )
        await utils.answer(message, text)

    # Вспомогательные методы
    async def _get_anime_data(self, query: str):
        try:
            response = requests.get(f"{self.jikan_url}/anime?q={query}&limit=1").json()
            if not response.get("data"):
                return None
                
            data = response["data"][0]
            return {
                "title": data["title"],
                "score": data["score"] if data["score"] else "N/A",
                "year": data["year"] if data["year"] else "N/A",
                "episodes": data["episodes"] if data["episodes"] else "N/A",
                "status": data["status"],
                "synopsis": data["synopsis"] if data["synopsis"] else "Нет описания",
                "image_url": data["images"]["jpg"]["image_url"]
            }
        except:
            return None