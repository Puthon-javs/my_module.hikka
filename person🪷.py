from hikkatl.types import Message
from .. import loader, utils
from datetime import datetime
import asyncio

@loader.tds
class QuickForwardMod(loader.Module):
    """Автоматическая пересылка сообщений из чатов в указанный чат"""
    strings = {
        "name": "QuickForward",
        "cfg_enabled": "Включить автопересылку",
        "cfg_target": "ID чата для пересылки",
        "cfg_delay": "Задержка пересылки (секунды)",
        "cfg_keywords": "Ключевые слова (через запятую)",
        "cfg_blacklist": "Чёрный список чатов (ID через запятую)",
        "status_on": "✅ <b>Автопересылка включена!</b>\n<b>Куда:</b> <code>{}</code>\n<b>Задержка:</b> <code>{} сек</code>",
        "status_off": "❌ <b>Автопересылка выключена!</b>",
        "no_target": "⚠️ <b>Укажите ID чата для пересылки!</b>",
        "invalid_id": "⚠️ <b>Некорректный ID чата!</b>",
        "added_blacklist": "➖ <b>Чат добавлен в чёрный список!</b> (ID: <code>{}</code>)",
        "removed_blacklist": "➕ <b>Чат удалён из чёрного списка!</b> (ID: <code>{}</code>)",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enabled",
                False,
                lambda: self.strings["cfg_enabled"],
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "target_chat",
                None,
                lambda: self.strings["cfg_target"],
                validator=loader.validators.TelegramID()
            ),
            loader.ConfigValue(
                "delay",
                5,
                lambda: self.strings["cfg_delay"],
                validator=loader.validators.Integer(minimum=0)
            ),
            loader.ConfigValue(
                "keywords",
                "",
                lambda: self.strings["cfg_keywords"],
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "blacklist",
                "",
                lambda: self.strings["cfg_blacklist"],
                validator=loader.validators.String()
            ),
        )

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message: Message):
        if not self.config["enabled"] or not self.config["target_chat"]:
            return

        # Проверка на чёрный список
        chat_id = utils.get_chat_id(message)
        if str(chat_id) in self.config["blacklist"].split(","):
            return

        # Проверка на ключевые слова (если они заданы)
        keywords = self.config["keywords"].lower().split(",") if self.config["keywords"] else []
        if keywords and not any(keyword in message.raw_text.lower() for keyword in keywords if message.raw_text):
            return

        # Задержка перед пересылкой
        await asyncio.sleep(self.config["delay"])

        try:
            await message.forward_to(self.config["target_chat"])
        except Exception:
            pass

    @loader.command(alias="fwstatus")
    async def forwardstatuscmd(self, message: Message):
        """Показать статус автопересылки"""
        if not self.config["enabled"] or not self.config["target_chat"]:
            await utils.answer(message, self.strings["status_off"])
            return

        await utils.answer(
            message,
            self.strings["status_on"].format(
                self.config["target_chat"],
                self.config["delay"]
            )
        )

    @loader.command(alias="fwon")
    async def forwardoncmd(self, message: Message):
        """Включить автопересылку"""
        args = utils.get_args_raw(message)
        if not args:
            if not self.config["target_chat"]:
                await utils.answer(message, self.strings["no_target"])
                return
        else:
            try:
                self.config["target_chat"] = int(args)
            except ValueError:
                await utils.answer(message, self.strings["invalid_id"])
                return

        self.config["enabled"] = True
        await self.forwardstatuscmd(message)

    @loader.command(alias="fwoff")
    async def forwardoffcmd(self, message: Message):
        """Выключить автопересылку"""
        self.config["enabled"] = False
        await utils.answer(message, self.strings["status_off"])

    @loader.command(alias="fwblacklist")
    async def forwardblacklistcmd(self, message: Message):
        """Добавить/удалить чат из чёрного списка"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "ℹ️ <b>Текущий чёрный список:</b> <code>{}</code>".format(self.config["blacklist"]))
            return

        chat_id = args.strip()
        blacklist = self.config["blacklist"].split(",")
        if chat_id in blacklist:
            blacklist.remove(chat_id)
            msg = self.strings["removed_blacklist"].format(chat_id)
        else:
            blacklist.append(chat_id)
            msg = self.strings["added_blacklist"].format(chat_id)

        self.config["blacklist"] = ",".join(filter(None, blacklist))
        await utils.answer(message, msg)