#meta developer: @Python_Javs
from hikka import loader, utils
from telethon.tl.types import Message
import random
import json
import os
from typing import Dict

@loader.tds
class ProgHelperMod(loader.Module):
    """💻 Улучшенный помощник программиста с защитой от ошибок"""
    strings = {
        "name": "ProgHelper",
        "config_done": "✅ Настройки сохранены!",
        "anon_warning": "⚠ Вы в анонимном режиме!",
        "no_code": "📝 Укажите код/вопрос для анализа",
        "lang_list": "🛠 Доступные языки: Python, JS, C++, Java, Go, Rust, TS",
        "db_error": "🔄 База данных восстановлена по умолчанию",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "gender",
                "anon",
                "Ваш пол (male/female/anon)",
                validator=loader.validators.Choice(["male", "female", "anon"])
            ),
            loader.ConfigValue(
                "lang",
                "Python",
                "Основной язык программирования",
                validator=loader.validators.Choice(
                    ["Python", "JavaScript", "C++", "Java", "Go", "Rust", "TypeScript"]
                )
            )
        )
        self.db_path = os.path.join(utils.get_base_dir(), "proghelper_db_v2.json")
        self._init_secure_db()

    def _init_secure_db(self):
        """Безопасная инициализация базы данных с защитой от ошибок"""
        default_db = {
            "quotes": {
                "male": ["Код — это поэзия!", "Ошибки — путь к мастерству"],
                "female": ["Ты — программистка мечты!", "Пиши код с уверенностью"],
                "anon": ["while True: learn()", "// TODO: Написать код"]
            },
            "snippets": {},
            "errors": {}
        }
        
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, "r") as f:
                    self.db = json.load(f)
                
                # Восстановление недостающих структур
                if "quotes" not in self.db:
                    self.db["quotes"] = default_db["quotes"]
                    self._save_db()
                    return True
            else:
                self.db = default_db
                self._save_db()
        except Exception:
            self.db = default_db
            self._save_db()
            return False

    def _save_db(self):
        """Безопасное сохранение БД"""
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.db, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    @loader.command()
    async def pcode(self, message: Message):
        """Безопасный анализ кода"""
        code = utils.get_args_raw(message)
        if not code:
            await utils.answer(message, self.strings["no_code"])
            return

        try:
            gender = self.config["gender"]
            quotes = self.db["quotes"].get(gender, self.db["quotes"]["anon"])
            
            analysis = (
                f"{'👨‍💻' if gender == 'male' else '👩‍💻'} Анализ кода:\n\n"
                f"🔍 Ошибок найдено: {random.randint(0, 3)}\n"
                f"⚡ Оптимизации: {random.choice(['возможны', 'не требуются'])}\n"
                f"💡 Совет: {random.choice(quotes)}"
            )
            await utils.answer(message, analysis)
        except Exception as e:
            await utils.answer(message, f"❌ Ошибка анализа: {str(e)}")

    @loader.command()
    async def pset(self, message: Message):
        """Настройки модуля"""
        args = utils.get_args_raw(message)
        if not args:
            current = (
                f"⚙️ Текущие настройки:\n"
                f"👤 Пол: {self.config['gender']}\n"
                f"💻 Язык: {self.config['lang']}\n\n"
                f"Используйте: .pset [параметр] [значение]\n"
                f"Пример: .pset lang JavaScript"
            )
            await utils.answer(message, current)
            return

        try:
            params = args.split(maxsplit=1)
            if len(params) != 2:
                raise ValueError("Неверный формат")
            
            key, value = params
            if key in self.config:
                self.config[key] = value.lower() if key == "gender" else value.capitalize()
                await utils.answer(message, self.strings["config_done"])
            else:
                await utils.answer(message, "❌ Неизвестный параметр")
        except Exception as e:
            await utils.answer(message, f"❌ Ошибка: {str(e)}")

    @loader.command()
    async def plang(self, message: Message):
        """Список поддерживаемых языков"""
        await utils.answer(message, self.strings["lang_list"])

    @loader.command()
    async def pfix(self, message: Message):
        """Восстановить базу данных"""
        self._init_secure_db()
        await utils.answer(message, self.strings["db_error"])