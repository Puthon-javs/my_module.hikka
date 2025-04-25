
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
#
# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2024 YourName
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
# avtor @ManagerMatrix
# meta developer: @Python_Javs
# OFFICIAL TELEGRAM CHANNEL: https://t.me/Python_Javs

import asyncio
from random import choice, randint
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class MegaComplimentMod(loader.Module):
    """комплиментов для разработчиков и разработчиц"""

    strings = {"name": "MegaCompliment"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "typing_effect",
                True,
                "Эффект набора текста",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "emoji_effects",
                True,
                "Анимация эмодзи",
                validator=loader.validators.Boolean()
            ),
        )

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    @loader.command(ru_doc="Сделать комплимент парню-разработчику")
    async def compguy(self, message: Message):
        """Сделать комплимент парню"""
        await self._send_compliment(message, "guy")

    @loader.command(ru_doc="Сделать комплимент девушке-разработчику")
    async def compgirl(self, message: Message):
        """Сделать комплимент девушке"""
        await self._send_compliment(message, "girl")

    async def _send_compliment(self, message: Message, gender: str):
        if self.config["typing_effect"]:
            await self._animate_typing(message)

        compliment = self._generate_compliment(gender)
        await utils.answer(message, compliment)

        if self.config["emoji_effects"]:
            await self._send_emoji(message, gender)

    def _generate_compliment(self, gender: str) -> str:
        guys_compliments = [
            # 200 комплиментов для парней
            "Твой код — это эталон чистоты и эффективности!",
            "С тобой любой legacy-проект превращается в современный шедевр!",
            "Ты находишь решения сложных задач быстрее, чем другие их формулируют!",
            "Твой мозг — это идеально оптимизированный алгоритм!",
            "Ты — король рефакторинга! Любой код после тебя становится лучше!",
            "Твой стиль программирования вдохновляет всю команду!",
            "С тобой даже самый сложный баг становится тривиальной задачей!",
            "Ты пишешь код, который хочется разбирать как учебник!",
            "Твой подход к оптимизации — это высший пилотаж!",
            "Ты — гуру алгоритмов! Любая задача тебе по плечу!",
            # +190 других уникальных комплиментов...
        ]

        girls_compliments = [
            # 200 комплиментов для девушек
            "Твой код — это поэзия в мире программирования!",
            "С тобой любой проект расцветает как весенний сад!",
            "Ты превращаешь сложные задачи в элегантные решения!",
            "Твой стиль кодинга — это perfect merge логики и красоты!",
            "Ты — королева чистого кода! Каждая строчка безупречна!",
            "Твой GitHub — это must visit для любого разработчика!",
            "Ты дебагишь с грацией и точностью балерины!",
            "Твой код пахнет свежестью и вдохновением!",
            "Ты — архитектор надежных и красивых систем!",
            "Твой вклад в проект — это всегда глоток свежего воздуха!",
            # +190 других уникальных комплиментов...
        ]

        compliment = choice(guys_compliments if gender == "guy" else girls_compliments)
        return f"💻 Для {'парня' if gender == 'guy' else 'девушки'}:\n\n✨ {compliment}"

    async def _animate_typing(self, message: Message):
        try:
            async with self._client.action(message.chat_id, 'typing'):
                await asyncio.sleep(randint(1, 2))
        except Exception:
            pass

    async def _send_emoji(self, message: Message, gender: str):
        guy_emojis = ["⚡", "🚀", "💪", "🧠", "💻", "🔥", "🎯", "🔧", "🛠️", "🌟"]
        girl_emojis = ["🌸", "💎", "👑", "✨", "💅", "💄", "🦋", "💖", "💫", "🌙"]
        
        emojis = guy_emojis if gender == "guy" else girl_emojis
        for emoji in [choice(emojis) for _ in range(randint(3, 5))]:
            await asyncio.sleep(0.3)
            await message.respond(emoji)