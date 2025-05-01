from hikkatl.types import Message
from .. import loader, utils
from datetime import datetime
import re

@loader.tds
class ChatToolsMod(loader.Module):
    """Мощные инструменты для управления чатами"""
    strings = {
        "name": "ChatTools",
        "welcome_enabled": "✅ <b>Приветствия включены!</b>",
        "welcome_disabled": "❌ <b>Приветствия выключены!</b>",
        "welcome_text": "👋 <b>Добро пожаловать, {user}!</b>\n\nПравила: /rules",
        "rules_set": "📜 <b>Правила чата установлены!</b>",
        "chat_cleared": "🧹 <b>Чат очищен!</b> (Удалено: {count} сообщений)",
        "no_admin": "⚠️ <b>Нужны права админа!</b>",
        "stats_header": "📊 <b>Статистика чата:</b>\n\n{stats}",
        "link_deleted": "🔗 <b>Удалена ссылка от:</b> @{username}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "welcome_enabled",
                True,
                lambda: "Включить приветствия",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "welcome_text",
                self.strings["welcome_text"],
                lambda: "Текст приветствия",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "rules_text",
                "📌 Правила чата:\n1. Без спама\n2. Без оскорблений",
                lambda: "Текст правил",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "ban_links",
                True,
                lambda: "Блокировать ссылки",
                validator=loader.validators.Boolean()
            ),
        )
        self.user_stats = {}

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message: Message):
        # Удаление ссылок
        if self.config["ban_links"] and "http" in (message.raw_text or ""):
            if await self.check_admin(utils.get_chat_id(message)):
                await message.delete()
                await self.log_action(
                    self.strings["link_deleted"].format(
                        username=message.sender.username or message.sender_id
                    )
                )

        # Статистика активности
        user_id = message.sender_id
        self.user_stats[user_id] = self.user_stats.get(user_id, 0) + 1

    @loader.command(alias="welcome")
    async def welcometogglecmd(self, message: Message):
        """Включить/выключить приветствия"""
        self.config["welcome_enabled"] = not self.config["welcome_enabled"]
        status = self.strings["welcome_enabled"] if self.config["welcome_enabled"] else self.strings["welcome_disabled"]
        await utils.answer(message, status)

    @loader.command(alias="setrules")
    async def setrulescmd(self, message: Message):
        """Установить правила чата"""
        args = utils.get_args_raw(message)
        if args:
            self.config["rules_text"] = args
        await utils.answer(message, self.strings["rules_set"])

    @loader.command(alias="clear")
    async def clearchatcmd(self, message: Message):
        """Очистить чат (только для админов)"""
        if not await self.check_admin(utils.get_chat_id(message)):
            await utils.answer(message, self.strings["no_admin"])
            return

        chat = await message.get_chat()
        count = 0
        async for msg in self.client.iter_messages(chat):
            if count >= 100:  # Лимит для безопасности
                break
            await msg.delete()
            count += 1
            await asyncio.sleep(0.5)  # Анти-флуд

        await utils.answer(
            message,
            self.strings["chat_cleared"].format(count=count)
        )

    @loader.command(alias="stats")
    async def chatstatscmd(self, message: Message):
        """Показать статистику чата"""
        if not self.user_stats:
            await utils.answer(message, "📊 <b>Статистика пуста!</b>")
            return

        sorted_stats = sorted(
            self.user_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Топ-10

        stats_text = "\n".join(
            f"▪ <b>{i+1}.</b> ID{user_id}: {count} сообщ."
            for i, (user_id, count) in enumerate(sorted_stats)
        )

        await utils.answer(
            message,
            self.strings["stats_header"].format(stats=stats_text)
        )

    async def check_admin(self, chat_id: int) -> bool:
        """Проверка прав админа"""
        try:
            chat = await self.client.get_entity(chat_id)
            return chat.admin_rights is not None
        except:
            return False

    async def log_action(self, text: str):
        """Логирование действий"""
        print(f"[ChatTools] {text}")  # Можно заменить на отправку в лог-чат