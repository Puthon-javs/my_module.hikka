
#meta developer: @Python_Javs

from .. import loader, utils
import random
import string
import secrets
from typing import Optional

@loader.tds
class PasswordGeneratorMod(loader.Module):
    """Генератор сверхсложных паролей с настройками"""

    strings = {
        "name": "PasswordGen",
        "cfg_demo": "Демо-режим (показывать примеры)",
        "cfg_min_len": "Минимальная длина пароля",
        "cfg_max_len": "Максимальная длина пароля",
        "cfg_use_special": "Использовать спецсимволы",
        "cfg_use_emoji": "Использовать emoji",
        "cfg_avoid_similar": "Избегать похожих символов",
        "generated": "<b>🔐 Сгенерированный пароль:</b> <code>{password}</code>\n"
                    "<b>📊 Длина:</b> {length}\n"
                    "<b>💪 Сложность:</b> {strength}",
        "no_args": "<b>❌ Укажите параметры генерации или используйте </b><code>.pgen default</code>",
        "presets": "<b>🎛 Доступные пресеты:</b>\n"
                  "<code>default</code> - 12 символов, буквы+цифры+спецсимволы\n"
                  "<code>strong</code> - 16 символов с максимальной сложностью\n"
                  "<code>pin</code> - 6 цифр\n"
                  "<code>memorable</code> - 8 слов с разделителями\n"
                  "<code>emoji</code> - пароль из emoji\n"
                  "<code>custom</code> - с вашими параметрами",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "demo_mode",
                True,
                lambda: self.strings["cfg_demo"],
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "min_length",
                8,
                lambda: self.strings["cfg_min_len"],
                validator=loader.validators.Integer(minimum=4, maximum=100)
            ),
            loader.ConfigValue(
                "max_length",
                24,
                lambda: self.strings["cfg_max_len"],
                validator=loader.validators.Integer(minimum=8, maximum=100)
            ),
            loader.ConfigValue(
                "use_special",
                True,
                lambda: self.strings["cfg_use_special"],
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "use_emoji",
                False,
                lambda: self.strings["cfg_use_emoji"],
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "avoid_similar",
                True,
                lambda: self.strings["cfg_avoid_similar"],
                validator=loader.validators.Boolean()
            ),
        )

    async def client_ready(self, client, db):
        self.client = client

    @staticmethod
    def calculate_entropy(password: str) -> float:
        """Вычисляет энтропию пароля в битах"""
        charset = 0
        if any(c.islower() for c in password):
            charset += 26
        if any(c.isupper() for c in password):
            charset += 26
        if any(c.isdigit() for c in password):
            charset += 10
        if any(c in string.punctuation for c in password):
            charset += 32
        if any(ord(c) > 0xffff for c in password):  # Emoji и другие не-BMP символы
            charset += 2048
        
        return len(password) * (charset ** 0.5) / 1.4427  # Логарифм по основанию 2

    def get_strength(self, entropy: float) -> str:
        """Оценивает сложность пароля"""
        if entropy > 120:
            return "Очень сильный 💪🔥"
        elif entropy > 80:
            return "Сильный 👍"
        elif entropy > 50:
            return "Средний 🤔"
        return "Слабый ⚠️"

    def generate_password(self, length: int, use_special: bool, use_emoji: bool, avoid_similar: bool) -> str:
        """Генерирует сложный пароль"""
        chars = []
        
        # Базовые наборы символов
        chars.extend(string.ascii_letters)
        chars.extend(string.digits)
        
        if use_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if avoid_similar:
                special_chars = special_chars.replace("l", "").replace("1", "").replace("I", "")
            chars.extend(special_chars)
        
        if use_emoji:
            emojis = ["🔑", "🔒", "🎯", "⚡", "🔥", "💎", "🛡", "👑", "🧠", "🦾"]
            chars.extend(emojis)
        
        if avoid_similar:
            chars = [c for c in chars if c not in "l1IoO0"]
        
        # Генерация с использованием криптографически безопасного генератора
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Гарантируем хотя бы один символ каждого выбранного типа
        if use_special and not any(c in string.punctuation for c in password):
            password = password[:-1] + secrets.choice(string.punctuation)
        if use_emoji and not any(ord(c) > 0xffff for c in password):
            password = password[:-1] + secrets.choice(emojis)
        
        return password

    @loader.command()
    async def pgen(self, message):
        """Сгенерировать пароль [preset|length]"""
        args = utils.get_args_raw(message)
        
        presets = {
            "default": (12, True, False, True),
            "strong": (16, True, False, True),
            "pin": (6, False, False, False),
            "memorable": (8, True, False, True),  # Генерация запоминающихся паролей
            "emoji": (8, False, True, False),
        }
        
        if not args:
            if self.config["demo_mode"]:
                examples = "\n".join(
                    f"<b>{preset}:</b> <code>{self.generate_password(*params)}</code>"
                    for preset, params in presets.items()
                )
                await utils.answer(
                    message,
                    f"{self.strings['presets']}\n\n<b>Примеры:</b>\n{examples}"
                )
            else:
                await utils.answer(message, self.strings["presets"])
            return
        
        if args in presets:
            length, use_special, use_emoji, avoid_similar = presets[args]
        elif args.isdigit():
            length = int(args)
            use_special = self.config["use_special"]
            use_emoji = self.config["use_emoji"]
            avoid_similar = self.config["avoid_similar"]
            length = max(self.config["min_length"], min(length, self.config["max_length"]))
        else:
            await utils.answer(message, self.strings["no_args"])
            return
        
        password = self.generate_password(length, use_special, use_emoji, avoid_similar)
        entropy = self.calculate_entropy(password)
        strength = self.get_strength(entropy)
        
        await utils.answer(
            message,
            self.strings["generated"].format(
                password=password,
                length=len(password),
                strength=strength
            )
        )

    @loader.command()
    async def pgenconfig(self, message):
        """Показать текущие настройки генератора"""
        config_text = (
            f"<b>⚙️ Текущие настройки генератора паролей:</b>\n\n"
            f"<b>Демо-режим:</b> {'вкл' if self.config['demo_mode'] else 'выкл'}\n"
            f"<b>Длина:</b> от {self.config['min_length']} до {self.config['max_length']}\n"
            f"<b>Спецсимволы:</b> {'вкл' if self.config['use_special'] else 'выкл'}\n"
            f"<b>Emoji:</b> {'вкл' if self.config['use_emoji'] else 'выкл'}\n"
            f"<b>Избегать похожих:</b> {'вкл' if self.config['avoid_similar'] else 'выкл'}\n\n"
            f"<i>Изменить настройки можно через </i><code>.config PasswordGen</code>"
        )
        await utils.answer(message, config_text)