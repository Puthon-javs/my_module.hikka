# meta developer: @Python_Javs
# meta banner: https://example.com/banner.jpg

import random
import time
from .. import loader, utils
from telethon.tl.types import Message

@loader.tds
class HackerAnimationMod(loader.Module):
    """Анимация взлома сервера с подбором логина и пароля"""

    strings = {
        "name": "HackAnim",
        "hacking": "🚀 <b>Начинаю взлом сервера...</b>",
        "success": "✅ <b>Взлом завершен!</b>\n\n<b>Логин:</b> <code>{login}</code>\n<b>Пароль:</b> <code>{password}</code>",
        "args": "❌ <b>Укажите цель для взлома!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "animation_delay",
                0.1,
                "Задержка между кадрами анимации",
                validator=loader.validators.Float(minimum=0.05, maximum=0.5)
            ),
        )

    async def client_ready(self, client, db):
        self._client = client

    @loader.unrestricted
    async def hackcmd(self, message: Message):
        """Взломать указанный сервер. Использование: .hack <цель>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args"))
            return

        await utils.answer(message, self.strings("hacking"))

        # Генерация случайного логина и пароля
        login = self._generate_credential()
        password = self._generate_credential(12)

        # Анимация взлома
        animation = [
            "🔍 Поиск уязвимостей...",
            "🛡️ Обход защиты...",
            "💻 Внедрение эксплойта...",
            "📡 Подключение к серверу...",
            "🔑 Подбор логина...",
            "🔓 Подбор пароля...",
            "📊 Анализ данных...",
            "🔄 Дешифровка...",
            "⚡ Получение доступа..."
        ]

        for step in animation:
            await utils.answer(message, f"🚀 <b>Взлом {args}...</b>\n\n{step}")
            time.sleep(self.config["animation_delay"] * 2)

            # Эффект "подбора" пароля
            for _ in range(3):
                fake_pass = self._generate_fake_password(len(password))
                msg = f"🚀 <b>Взлом {args}...</b>\n\n{step}\n\n🔑 Попытка входа: <code>{login}</code>\n🔓 Пароль: <code>{fake_pass}</code>"
                await utils.answer(message, msg)
                time.sleep(self.config["animation_delay"])

        # Финальное сообщение с "найденными" данными
        await utils.answer(message, self.strings("success").format(login=login, password=password))

    def _generate_credential(self, length=8):
        """Генерация случайного логина или пароля"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_fake_password(self, length):
        """Генерация случайного пароля для анимации"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
        return ''.join(random.choice(chars) for _ in range(length))