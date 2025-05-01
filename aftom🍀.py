from hikkatl.types import Message
from .. import loader, utils
import asyncio

@loader.tds
class SmartReplierMod(loader.Module):
    """Умные автоответы на сообщения по ключевым словам"""
    strings = {
        "name": "SmartReplier",
        "reply_added": "✅ <b>Автоответ добавлен!</b>\n<b>Триггер:</b> <code>{}</code>\n<b>Ответ:</b> <code>{}</code>",
        "reply_removed": "🗑 <b>Автоответ удалён!</b> (ID: <code>{}</code>)",
        "no_replies": "📭 <b>Нет сохранённых автоответов.</b>",
        "replies_list": "📋 <b>Список автоответов:</b>\n\n{}",
        "not_found": "🔍 <b>Автоответ не найден!</b>",
        "args_error": "❌ <b>Используйте:</b> <code>.addreply триггер | ответ</code>",
        "ignore_added": "➖ <b>Чат добавлен в игнор-лист!</b> (ID: <code>{}</code>)",
        "ignore_removed": "➕ <b>Чат удалён из игнор-листа!</b> (ID: <code>{}</code>)",
    }

    def __init__(self):
        self.replies = {}
        self.ignore_list = set()

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message: Message):
        if not self.replies or utils.get_chat_id(message) in self.ignore_list:
            return

        text = message.raw_text.lower() if message.raw_text else ""
        for trigger, reply in self.replies.items():
            if trigger.lower() in text:
                await asyncio.sleep(1)  # Задержка для избежания флуда
                await utils.answer(message, reply)
                break

    @loader.command(alias="addreply")
    async def addreplycmd(self, message: Message):
        """Добавить автоответ. Пример: .addreply привет | Hello!"""
        args = utils.get_args_raw(message)
        if not args or "|" not in args:
            await utils.answer(message, self.strings["args_error"])
            return

        trigger, reply = args.split("|", 1)
        trigger = trigger.strip()
        reply = reply.strip()

        self.replies[trigger] = reply
        await utils.answer(
            message,
            self.strings["reply_added"].format(trigger, reply)
        )

    @loader.command(alias="delreply")
    async def delreplycmd(self, message: Message):
        """Удалить автоответ. Пример: .delreply привет"""
        args = utils.get_args_raw(message)
        if not args or args not in self.replies:
            await utils.answer(message, self.strings["not_found"])
            return

        del self.replies[args]
        await utils.answer(
            message,
            self.strings["reply_removed"].format(args)
        )

    @loader.command(alias="listreplies")
    async def listrepliescmd(self, message: Message):
        """Список всех автоответов"""
        if not self.replies:
            await utils.answer(message, self.strings["no_replies"])
            return

        replies_list = "\n".join(
            f"▪ <code>{trigger}</code> → <code>{reply}</code>"
            for trigger, reply in self.replies.items()
        )
        await utils.answer(
            message,
            self.strings["replies_list"].format(replies_list)
        )

    @loader.command(alias="ignorechat")
    async def ignorechatcmd(self, message: Message):
        """Добавить/удалить чат из игнор-листа"""
        chat_id = utils.get_chat_id(message)
        if chat_id in self.ignore_list:
            self.ignore_list.remove(chat_id)
            msg = self.strings["ignore_removed"].format(chat_id)
        else:
            self.ignore_list.add(chat_id)
            msg = self.strings["ignore_added"].format(chat_id)

        await utils.answer(message, msg)