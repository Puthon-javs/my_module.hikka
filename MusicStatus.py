
#  ╔════════════════════════════════════════════╗
#  ║                                                   ║
#  ║   ██████╗ ██╗   ██╗████████╗██╗  ██╗         ║       #  ║   ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║        ║
#  ║   ██████╔╝ ╚████╔╝    ██║   ███████║         ║
#  ║   ██╔═══╝   ╚██╔╝     ██║   ██╔══██║         ║
#  ║   ██║        ██║      ██║   ██║  ██║          ║
#  ║   ╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝          ║
#  ║                                                  ║
#  ║   ███████╗ ██████╗██████╗ ██╗████████╗    ║
#  ║   ██╔════╝██╔════╝██╔══██╗██║╚══██╔══╝    ║
#  ║   ███████╗██║     ██████╔╝██║   ██║        ║
#  ║   ╚════██║██║     ██╔══██╗██║   ██║         ║
#  ║   ███████║╚██████╗██║  ██║██║   ██║         ║
#  ║   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝   ╚═╝          ║
#  ║                                                   ║
#  ║   Microsoft Python Script v1.0              ║
#  ╚════════════════════════════════════════════╝
#                      © Copyright 2025


# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2024 YourName
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
# avtor @ManagerMatrix
# meta developer: @Python_Javs
# OFFICIAL TELEGRAM CHANNEL: https://t.me/Python_Javs


from .. import loader, utils
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.users import GetFullUserRequest
from hikkatl.types import Message
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class MusicBioMod(loader.Module):
    """Автоматическое обновление био с информацией о треке"""

    strings = {
        "name": "MusicBio",
        "on": "🎵 Музыкальный статус включен. Трек: {} - {}",
        "off": "🔇 Музыкальный статус выключен. Био восстановлено",
        "set": "✅ Трек установлен: {} - {}",
        "no_audio": "❌ Это не аудиофайл",
        "no_meta": "❌ В аудио нет метаданных (исполнитель/название)",
        "current": "🎵 Текущий трек: {} - {}",
        "not_active": "⚠️ Музыкальный статус выключен. Включите (.музон)",
        "bio_updated": "✅ Био успешно обновлено",
        "bio_restored": "✅ Исходное био восстановлено"
    }

    def __init__(self):
        self.original_bio = ""
        self.is_active = False
        self.current_track = None
        self.bio_limit = 70  # Лимит символов для обычных аккаунтов

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        # Получаем и сохраняем оригинальное био
        try:
            user = await self.client(GetFullUserRequest(self.client.tg_id))
            self.original_bio = user.full_user.about or ""
            self.bio_limit = 140 if user.users[0].premium else 70
            logger.info("Оригинальное био сохранено")
        except Exception as e:
            logger.error(f"Ошибка при получении био: {e}")

    async def update_bio(self, text: str):
        """Обновляет био с обработкой ошибок"""
        try:
            text = text[:self.bio_limit]  # Обрезаем по лимиту
            await self.client(UpdateProfileRequest(about=text))
            logger.info(f"Био обновлено: {text}")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления био: {e}")
            return False

    async def restore_bio(self):
        """Восстанавливает оригинальное био"""
        if self.original_bio:
            success = await self.update_bio(self.original_bio)
            if success:
                logger.info("Оригинальное био восстановлено")
                return True
        return False

    async def get_track_info(self, message: Message):
        """Извлекает метаданные трека из аудио"""
        if not message.audio:
            return None
            
        for attr in message.audio.attributes:
            if hasattr(attr, 'performer') and hasattr(attr, 'title'):
                performer = getattr(attr, 'performer', '').strip()
                title = getattr(attr, 'title', '').strip()
                if performer and title:
                    return (performer, title)
        return None

    @loader.command(alias="музон")
    async def musicon(self, message: Message):
        """Включить музыкальное био"""
        if not self.current_track:
            await utils.answer(message, "⚠️ Сначала установите трек (.музставь)")
            return
            
        self.is_active = True
        artist, title = self.current_track
        success = await self.update_bio(f"🎵 {artist} - {title}")
        
        if success:
            await utils.answer(message, self.strings["on"].format(artist, title))
        else:
            await utils.answer(message, "❌ Не удалось обновить био")

    @loader.command(alias="музвыкл")
    async def musicoff(self, message: Message):
        """Выключить музыкальное био"""
        self.is_active = False
        success = await self.restore_bio()
        
        if success:
            await utils.answer(message, self.strings["off"])
        else:
            await utils.answer(message, "❌ Не удалось восстановить био")

    @loader.command(alias="музставь")
    async def setmusic(self, message: Message):
        """Установить трек из аудио (реплай)"""
        if not message.is_reply:
            await utils.answer(message, "❌ Ответьте на сообщение с аудиофайлом")
            return
            
        reply = await message.get_reply_message()
        track = await self.get_track_info(reply)
        
        if not track:
            await utils.answer(message, self.strings["no_audio"])
            return
            
        artist, title = track
        if not artist or not title:
            await utils.answer(message, self.strings["no_meta"])
            return
            
        self.current_track = (artist, title)
        
        if self.is_active:
            success = await self.update_bio(f"🎵 {artist} - {title}")
            if success:
                await utils.answer(message, self.strings["set"].format(artist, title))
            else:
                await utils.answer(message, "❌ Не удалось обновить био")
        else:
            await utils.answer(message, 
                f"{self.strings['set'].format(artist, title)}\n"
                f"{self.strings['not_active']}"
            )

    @loader.command(alias="музтекущий")
    async def currenttrack(self, message: Message):
        """Показать текущий трек и статус"""
        if self.current_track:
            artist, title = self.current_track
            status = "включен" if self.is_active else "выключен"
            await utils.answer(
                message,
                f"{self.strings['current'].format(artist, title)}\n"
                f"Статус: {status}"
            )
        else:
            await utils.answer(message, "❌ Трек не установлен")

async def register():
    return MusicBioMod()