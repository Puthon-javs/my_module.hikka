from hikkatl.types import Message
from .. import loader, utils
import json
import os
from datetime import datetime

@loader.tds
class SmartSaverMod(loader.Module):
    """Автоматически сохраняет важные сообщения"""
    strings = {
        "name": "SmartSaver",
        "saved": "💾 <b>Сохранено в категорию</b> <code>{}</code>!",
        "no_keywords": "❌ <b>Нет ключевых слов для сохранения!</b>",
        "show_saved": "📂 <b>Сохранённые данные:</b>\n\n{}",
        "empty": "📭 <b>В этой категории ничего нет</b>",
        "deleted": "🗑 <b>Удалено {} записей</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "keywords",
                "важно,срочно,сохрани",
                lambda: "Ключевые слова через запятую",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "auto_save",
                True,
                lambda: "Автосохранение при обнаружении ключевых слов",
                validator=loader.validators.Boolean()
            ),
        )
        self.data_file = "smartsaver_data.json"
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_file):
            return {"text": [], "photo": [], "link": [], "document": []}
        
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    async def watcher(self, message: Message):
        if not self.config["auto_save"] or not message.text:
            return

        keywords = [k.strip().lower() for k in self.config["keywords"].split(",")]
        text = message.text.lower()
        
        if any(keyword in text for keyword in keywords):
            category = self._detect_category(message)
            if category:
                self._save_message(message, category)

    def _detect_category(self, message: Message) -> str:
        """Определяет категорию сообщения"""
        if message.photo:
            return "photo"
        elif message.document:
            return "document"
        elif "http://" in message.text or "https://" in message.text:
            return "link"
        return "text"

    def _save_message(self, message: Message, category: str):
        """Сохраняет сообщение в указанную категорию"""
        save_data = {
            "text": message.text,
            "date": str(datetime.now()),
            "chat": utils.get_chat_id(message),
            "sender": message.sender_id
        }
        self.data[category].append(save_data)
        self._save_data()

    @loader.command(alias="ssave")
    async def savemancmd(self, message: Message):
        """Вручную сохранить сообщение (ответьте на него)"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, "❌ <b>Ответьте на сообщение для сохранения!</b>")
            return

        category = self._detect_category(reply)
        self._save_message(reply, category)
        await utils.answer(
            message,
            self.strings["saved"].format(category)
        )

    @loader.command(alias="sshow")
    async def showdatacmd(self, message: Message):
        """Показать сохранённые данные (можно указать категорию)"""
        args = utils.get_args_raw(message)
        category = args.lower() if args else None

        if category and category in self.data:
            items = self.data[category]
            if not items:
                await utils.answer(message, self.strings["empty"])
                return
                
            result = "\n".join(
                f"▪ {item['date']}: {item['text'][:50]}..."
                for item in items[-10:]  # Последние 10 записей
            )
        else:
            result = ""
            for cat, items in self.data.items():
                result += f"\n▫ <b>{cat}</b>: {len(items)} записей\n"

        await utils.answer(
            message,
            self.strings["show_saved"].format(result)
        )

    @loader.command(alias="sclear")
    async def cleardatacmd(self, message: Message):
        """Очистить данные (можно указать категорию)"""
        args = utils.get_args_raw(message)
        if args and args in self.data:
            count = len(self.data[args])
            self.data[args] = []
            msg = self.strings["deleted"].format(count)
        else:
            total = 0
            for cat in self.data:
                total += len(self.data[cat])
                self.data[cat] = []
            msg = self.strings["deleted"].format(f"все {total}")

        self._save_data()
        await utils.answer(message, msg)