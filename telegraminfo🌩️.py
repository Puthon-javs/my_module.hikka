# meta developer: @Python_Javs

from hikkatl.tl.types import User
from hikkatl.tl.functions.users import GetFullUserRequest
from hikkatl.tl.functions.help import GetConfigRequest
from hikkatl.tl.functions.account import GetAuthorizationsRequest
from .. import loader, utils
import random

@loader.tds
class ClientInfoSecureMod(loader.Module):
    """Информация о клиенте с настройками приватности"""

    strings = {
        "name": "ClientInfoSecure",
        "cfg_hide_phone": "Скрыть настоящий номер телефона",
        "cfg_fake_phone": "Показывать фейковый номер",
        "cfg_hide_location": "Скрыть настоящий IP/страну сессий",
        "cfg_fake_location": "Подменять IP/страну в сессиях",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "hide_phone",
                False,
                lambda: self.strings["cfg_hide_phone"],
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "fake_phone",
                False,
                lambda: self.strings["cfg_fake_phone"],
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "hide_location",
                False,
                lambda: self.strings["cfg_hide_location"],
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "fake_location",
                False,
                lambda: self.strings["cfg_fake_location"],
                validator=loader.validators.Boolean(),
            ),
        )

    async def clientinfocmd(self, message):
        """Получить информацию (с учётом настроек приватности)"""
        me = await self.client.get_me()
        full = await self.client(GetFullUserRequest(me))
        auths = await self.client(GetAuthorizationsRequest())

        # Обработка номера телефона
        phone = f"+{me.phone}"
        if self.config["hide_phone"] and not self.config["fake_phone"]:
            phone = "скрыто"
        elif self.config["fake_phone"]:
            phone = f"+7{random.randint(9000000000, 9999999999)}"

        # Генерация фейковых локаций
        fake_countries = ["USA", "Germany", "Japan", "Brazil", "Russia"]
        fake_ips = [
            f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.1",
        ]

        client_info = (
            "🛜 <b>Информация о Telegram</b>\n\n"
            f"👤 <b>Имя:</b> {me.first_name}\n"
            f"📛 <b>Фамилия:</b> {me.last_name or 'Нет'}\n"
            f"🔗 <b>Юзернейм:</b> @{me.username or 'Нет'}\n"
            f"🆔 <b>ID:</b> <code>{me.id}</code>\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"📝 <b>Био:</b> {full.full_user.about or 'Нет'}\n\n"
            "📡 <b>Активные сессии:</b>\n"
        )

        for i, auth in enumerate(auths.authorizations, 1):
            country = auth.country
            ip = auth.ip

            if self.config["hide_location"] and not self.config["fake_location"]:
                country = "скрыто"
                ip = "скрыто"
            elif self.config["fake_location"]:
                country = random.choice(fake_countries)
                ip = random.choice(fake_ips)

            client_info += (
                f"  {i}. <b>{auth.app_name} {auth.app_version}</b>\n"
                f"  📱 <i>{auth.device_model} ({auth.system_version})</i>\n"
                f"  🌐 <i>{country} (IP: {ip})</i>\n"
                f"  🕒 <i>{auth.date_created.strftime('%d.%m.%Y %H:%M')}</i>\n\n"
            )

        await utils.answer(message, client_info)