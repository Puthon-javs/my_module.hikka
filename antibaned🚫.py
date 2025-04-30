from hikkatl.types import Message
from hikkatl.tl.functions.messages import DeleteMessagesRequest
from hikkatl.utils import get_display_name
from .. import loader, utils
import time
from collections import defaultdict


@loader.tds
class AntiTelegramRulesMod(loader.Module):
    """Модуль для автоматического удаления сообщений, нарушающих правила Telegram"""
    
    strings = {
        "name": "AntiTelegramRules",
        "enabled": "✅ <b>Анти-правила Telegram включены</b>\nВсе подозрительные сообщения будут автоматически удаляться",
        "disabled": "❌ <b>Анти-правила Telegram выключены</b>",
        "deleted": "🗑 <b>Удалено сообщение, которое могло нарушать правила Telegram</b>\nПричина: <code>{}</code>",
        "stats": "📊 <b>Статистика AntiTelegramRules:</b>\n"
                "• Удалено сообщений: <code>{}</code>\n"
                "• Последнее удаление: <code>{}</code> назад\n"
                "• Последняя причина: <code>{}</code>",
        "flood_warn": "⚠️ <b>Прекратите флудить!</b>\nСледующее сообщение будет удалено!",
        "insult_warn": "⚠️ <b>Не используйте оскорбления!</b>\nСообщение было удалено!",
    }

    strings_ru = strings

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enabled",
                True,
                lambda: "Включить автоматическое удаление опасных сообщений",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "delete_own",
                True,
                lambda: "Удалять собственные опасные сообщения",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "delete_others",
                True,
                lambda: "Удалять опасные сообщения от других",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "keywords",
                ["спам", "фишинг", "взлом", "взломать", "ddos", "хак", "наркотики", "оружие"],
                lambda: "Ключевые слова для удаления",
                validator=loader.validators.Series()
            ),
            loader.ConfigValue(
                "insults",
                ["дурак", "идиот", "дебил", "тупой", "лох", "придурок", "кретин"],
                lambda: "Список оскорблений",
                validator=loader.validators.Series()
            ),
            loader.ConfigValue(
                "max_message_length",
                2000,
                lambda: "Максимальная длина сообщения (символов)",
                validator=loader.validators.Integer(minimum=100, maximum=5000)
            ),
            loader.ConfigValue(
                "flood_time",
                5,
                lambda: "Время между сообщениями для антифлуда (секунды)",
                validator=loader.validators.Integer(minimum=1, maximum=60)
            ),
            loader.ConfigValue(
                "flood_count",
                5,
                lambda: "Количество сообщений подряд для антифлуда",
                validator=loader.validators.Integer(minimum=2, maximum=20)
            ),
            loader.ConfigValue(
                "report_to_admins",
                False,
                lambda: "Отправлять уведомление админам при удалении",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "warn_before_delete",
                True,
                lambda: "Предупреждать перед удалением",
                validator=loader.validators.Boolean()
            )
        )
        self.stats = {
            "total_deleted": 0,
            "last_deleted": None,
            "last_reason": None,
            "flood_data": defaultdict(lambda: {"count": 0, "last_time": 0}),
            "user_last_message": {}
        }

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    @loader.command(ru_doc="Включить защиту от ограничений Telegram")
    async def atr_on(self, message: Message):
        """Enable Anti-Telegram Rules protection"""
        self.config["enabled"] = True
        await utils.answer(message, self.strings("enabled"))

    @loader.command(ru_doc="Выключить защиту от ограничений Telegram")
    async def atr_off(self, message: Message):
        """Disable Anti-Telegram Rules protection"""
        self.config["enabled"] = False
        await utils.answer(message, self.strings("disabled"))

    @loader.command(ru_doc="Показать статистику удалений")
    async def atr_stats(self, message: Message):
        """Show deletion statistics"""
        last_deleted = "никогда"
        if self.stats["last_deleted"]:
            last_deleted = utils.format_timedelta(utils.get_time() - self.stats["last_deleted"])
        
        await utils.answer(
            message,
            self.strings("stats").format(
                self.stats["total_deleted"],
                last_deleted,
                self.stats["last_reason"] or "неизвестно"
            )
        )

    async def watcher(self, message: Message):
        if not self.config["enabled"]:
            return

        if not isinstance(message, Message):
            return

        # Проверка на флуд
        flood_reason = await self.check_flood(message)
        if flood_reason:
            await self.delete_message(message, flood_reason)
            return

        # Проверка на оскорбления
        insult_reason = await self.check_insults(message)
        if insult_reason:
            if self.config["warn_before_delete"]:
                await message.respond(self.strings("insult_warn"))
            await self.delete_message(message, insult_reason)
            return

        # Общая проверка сообщения
        danger_reason = await self.check_message(message)
        if danger_reason:
            await self.delete_message(message, danger_reason)

    async def check_flood(self, message: Message) -> str:
        """Проверка на флуд"""
        user_id = message.sender_id
        chat_id = utils.get_chat_id(message)
        now = time.time()
        
        # Обновляем данные о флуде
        flood_key = f"{chat_id}_{user_id}"
        flood_data = self.stats["flood_data"][flood_key]
        
        if now - flood_data["last_time"] > self.config["flood_time"]:
            flood_data["count"] = 1
        else:
            flood_data["count"] += 1
        
        flood_data["last_time"] = now
        
        # Проверяем превышение лимита
        if flood_data["count"] >= self.config["flood_count"]:
            if self.config["warn_before_delete"] and flood_data["count"] == self.config["flood_count"]:
                await message.respond(self.strings("flood_warn"))
                return None
            return f"Флуд ({flood_data['count']} сообщений за {self.config['flood_time']} сек)"
        
        return None

    async def check_insults(self, message: Message) -> str:
        """Проверка на оскорбления"""
        text = utils.get_args_raw(message) or ""
        text_lower = text.lower()
        
        for insult in self.config["insults"]:
            if insult.lower() in text_lower:
                return f"Оскорбление ({insult})"
        
        return None

    async def check_message(self, message: Message) -> str:
        """Проверка сообщения на опасный контент"""
        text = utils.get_args_raw(message) or ""
        
        # Проверка длины сообщения
        if len(text) > self.config["max_message_length"]:
            return f"Слишком длинное сообщение ({len(text)} символов)"
        
        # Проверка ключевых слов
        text_lower = text.lower()
        for keyword in self.config["keywords"]:
            if keyword.lower() in text_lower:
                return f"Запрещенное слово ({keyword})"
        
        return None

    async def delete_message(self, message: Message, reason: str):
        """Удаление опасного сообщения"""
        try:
            await message.delete()
            
            self.stats["total_deleted"] += 1
            self.stats["last_deleted"] = utils.get_time()
            self.stats["last_reason"] = reason
            
            if self.config["report_to_admins"]:
                await message.respond(self.strings("deleted").format(reason))
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")

    @loader.command(ru_doc="Проверить сообщение на опасный контент")
    async def atr_check(self, message: Message):
        """Check message for dangerous content"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, "❌ Нет сообщения для проверки")
            return
        
        checks = [
            ("Флуд", await self.check_flood(reply)),
            ("Оскорбления", await self.check_insults(reply)),
            ("Опасный контент", await self.check_message(reply)),
        ]
        
        results = []
        for check_name, result in checks:
            if result:
                results.append(f"⚠️ {check_name}: {result}")
        
        if results:
            await utils.answer(message, "\n".join(results))
        else:
            await utils.answer(message, "✅ Сообщение безопасно")

    @loader.command(ru_doc="Очистить историю флуда")
    async def atr_clearflood(self, message: Message):
        """Clear flood history"""
        self.stats["flood_data"].clear()
        await utils.answer(message, "✅ История флуда очищена")