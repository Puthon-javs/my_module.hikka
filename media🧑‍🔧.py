from hikkatl.types import Message
from .. import loader, utils
import time

@loader.tds
class MediaGuardMod(loader.Module):
    """Автоматически удаляет медиа от неразрешённых пользователей"""
    strings = {
        "name": "MediaGuard",
        "cfg_enabled": "Включить защиту медиа",
        "cfg_whitelist": "Белый список (ID через запятую)",
        "cfg_ban_types": "Типы файлов для блокировки (photo,video,gif,document)",
        "cfg_log_chat": "ID чата для логов (0 = отключено)",
        "media_deleted": "🚫 <b>Медиа удалено!</b>\n<b>Чат:</b> <code>{}</code>\n<b>Отправитель:</b> <code>{}</code>",
        "whitelist_added": "✅ <b>Добавлен в белый список:</b> <code>{}</code>",
        "whitelist_removed": "🗑 <b>Удалён из белого списка:</b> <code>{}</code>",
        "status": "🔒 <b>MediaGuard {}</b>\n<b>Белый список:</b> {}\n<b>Логи:</b> {}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "enabled",
                True,
                lambda: self.strings["cfg_enabled"],
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "whitelist",
                "",
                lambda: self.strings["cfg_whitelist"],
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "ban_types",
                "photo,video,document",
                lambda: self.strings["cfg_ban_types"],
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "log_chat",
                0,
                lambda: self.strings["cfg_log_chat"],
                validator=loader.validators.TelegramID()
            ),
        )

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message: Message):
        if not self.config["enabled"]:
            return

        chat_id = utils.get_chat_id(message)
        user_id = message.sender_id
        whitelist = set(map(int, self.config["whitelist"].split(","))) if self.config["whitelist"] else set()

        # Проверка на белый список и права
        if user_id in whitelist or await self.check_admin(chat_id):
            return

        # Проверка типа медиа
        media_type = self.get_media_type(message)
        if media_type and media_type in self.config["ban_types"].split(","):
            await message.delete()
            log_msg = self.strings["media_deleted"].format(chat_id, user_id)
            await self.log_action(log_msg)

    async def check_admin(self, chat_id: int) -> bool:
        """Проверяет, есть ли у бота права админа в чате"""
        try:
            chat = await self.client.get_entity(chat_id)
            return chat.admin_rights is not None
        except:
            return False

    def get_media_type(self, message: Message) -> str | None:
        """Определяет тип медиа в сообщении"""
        if message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.gif:
            return "gif"
        elif message.document:
            return "document"
        return None

    async def log_action(self, text: str):
        """Отправляет логи в указанный чат"""
        if self.config["log_chat"]:
            await self.client.send_message(
                self.config["log_chat"],
                text
            )

    @loader.command(alias="mgstatus")
    async def mediaguardstatuscmd(self, message: Message):
        """Показать статус защиты"""
        status = "ВКЛ" if self.config["enabled"] else "ВЫКЛ"
        whitelist = self.config["whitelist"] or "нет"
        logs = "ВКЛ" if self.config["log_chat"] else "ВЫКЛ"

        await utils.answer(
            message,
            self.strings["status"].format(status, whitelist, logs)
        )

    @loader.command(alias="mgwl")
    async def mediaguardwlcmd(self, message: Message):
        """Добавить/удалить пользователя из белого списка"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            await utils.answer(message, "❌ <b>Укажите ID пользователя!</b>")
            return

        user_id = int(args)
        whitelist = set(map(int, self.config["whitelist"].split(","))) if self.config["whitelist"] else set()

        if user_id in whitelist:
            whitelist.remove(user_id)
            msg = self.strings["whitelist_removed"].format(user_id)
        else:
            whitelist.add(user_id)
            msg = self.strings["whitelist_added"].format(user_id)

        self.config["whitelist"] = ",".join(map(str, whitelist))
        await utils.answer(message, msg)