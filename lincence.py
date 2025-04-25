#  ╔════════════════════════════════════════════╗
#  ║          UserBot License Module            ║
#  ║        for Hikka Telegram Userbot          ╕
#  ╚════════════════════════════════════════════╝
#  © 2024 | @Python_Javs
# avtor @ManagerMatrix
# meta developer: @Python_Javs

from .. import loader, utils
from telethon.tl.types import Message
import asyncio

@loader.tds
class LicenseModule(loader.Module):
    """Модуль лицензионного соглашения"""

    strings = {
        "name": "LicenseMod",
        "cfg_company": "Название вашей компании",
        "cfg_channel": "Ссылка на ваш канал",
        "license_text": (
            "╔════ {company} ═════╗\n"
            "║ ✅ Коммерческое использование\n"
            "║ ✅ Разрешается модификация\n"
            "║ ℹ️ Сохранять копирайт\n"
            "║ ⚠️ Без гарантий\n"
            "║ ⚠️ Пользователь принимает риски\n"
            "║ Официальный канал: {channel}\n"
            "╚═══════════════════╝"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "company",
                "MyCompany",
                lambda: self.strings["cfg_company"],
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "channel",
                "t.me/Python_Javs",
                lambda: self.strings["cfg_channel"],
                validator=loader.validators.String(),
            ),
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def show_license(self, message: Message):
        """Показать лицензионное соглашение"""
        license_text = self.strings["license_text"].format(
            company=self.config["company"],
            channel=self.config["channel"],
        )
        await utils.answer(message, license_text)

    @loader.command(ru_doc="Показать лицензионное соглашение")
    async def licensecmd(self, message: Message):
        """Показать лицензию"""
        await self.show_license(message)

    @loader.command(ru_doc="Настроить параметры лицензии")
    async def licenseset(self, message: Message):
        """Открыть настройки"""
        await self.invoke("config", self.strings["name"], message.peer_id)

async def register():
    return LicenseModule()