from hikkatl.types import Message, User
from hikkatl.utils import get_display_name
from hikkatl.tl.functions.channels import EditBannedRequest
from hikkatl.tl.functions.photos import UploadProfilePhotoRequest
from hikkatl.tl.types import ChatBannedRights
from datetime import datetime, timedelta
import requests
from io import BytesIO
from .. import loader, utils

@loader.tds
class UserStatusUltimateMod(loader.Module):
    """Улучшенный модуль управления статусами и баннерами"""

    strings = {
        "name": "UserStatusUltimate",
        "status_set": "✅ <b>Статус {} установлен для {}</b>",
        "no_reply": "🚫 <b>Ответьте на сообщение пользователя!</b>",
        "banned": "⛔ <b>{} получил бан на 1 день!</b>",
        "muted": "🔇 <b>{} получил мут на 5 минут!</b>",
        "kicked": "👢 <b>{} был кикнут!</b>",
        "no_rights": "🚫 <b>Недостаточно прав!</b>",
        "banner_set": "🖼 <b>Баннер успешно обновлён!</b>",
        "banner_fail": "🚫 <b>Не удалось установить баннер</b>",
        "config_banner": "🌅 <b>URL баннера обновлён!</b>",
        "profile": (
            "🖼 <b>Баннер профиля:</b>\n\n"
            "🗓 <b>Полная информация:</b>\n\n"
            "🆔 <b>ID:</b> <code>{}</code>\n"
            "👤 <b>Имя:</b> {}\n"
            "📛 <b>Юзернейм:</b> {}\n"
            "⭐ <b>Статус:</b> {}\n"
            "🤖 <b>Бот:</b> {}\n"
            "✅ <b>Верификация:</b> {}\n"
            "🚫 <b>Ограничения:</b> {}"
        )
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "banner_url",
                "https://i.imgur.com/xNQhfLZ.jpeg",
                "URL баннера профиля",
                validator=loader.validators.Link()
            )
        )
        self.statuses = {
            "standard": "Standard VIP",
            "vip": "VIP",
            "gold": "Gold VIP",
            "platinum": "Platinum VIP",
            "admin": "Administrator"
        }
        self.users_status = {}

    async def client_ready(self, client, db):
        self._client = client

    @loader.command()
    async def setbanner(self, message: Message):
        """- Установить баннер из настроек"""
        try:
            response = requests.get(self.config["banner_url"])
            if response.status_code != 200:
                raise Exception("Ошибка загрузки изображения")
            
            # Исправление ошибки decode
            file = BytesIO(response.content)
            file.name = "banner.jpg"
            
            # Изменено для исправления ошибки decode
            uploaded = await self._client.upload_file(file)
            await self._client(UploadProfilePhotoRequest(
                file=uploaded,
                video_emoji_markup=None
            ))
            await utils.answer(message, self.strings["banner_set"])
        except Exception as e:
            await utils.answer(
                message,
                f"{self.strings['banner_fail']}\n"
                f"<b>Ошибка:</b> <code>{str(e)}</code>\n"
                f"<b>Текущий URL:</b> <code>{self.config['banner_url']}</code>"
            )

    # Все остальные методы остаются БЕЗ ИЗМЕНЕНИЙ
    @loader.command()
    async def profile(self, message: Message):
        """(reply) - Показать профиль"""
        reply = await message.get_reply_message()
        user = message.sender_id if not reply else reply.sender_id

        entity = await self._client.get_entity(user)
        
        await utils.answer(
            message,
            self.strings["profile"].format(
                user,
                get_display_name(entity),
                f"@{entity.username}" if entity.username else "Нет",
                self.users_status.get(user, "Нет статуса"),
                "Да" if getattr(entity, "bot", False) else "Нет",
                "Да" if getattr(entity, "verified", False) else "Нет",
                "Да" if getattr(entity, "restricted", False) else "Нет"
            )
        )

    @loader.command()
    async def ban(self, message: Message):
        """(reply) - Забанить на 1 день"""
        await self._mod_action(message, "banned", timedelta(days=1), view_messages=True)

    @loader.command()
    async def mute(self, message: Message):
        """(reply) - Замутить на 5 минут"""
        await self._mod_action(message, "muted", timedelta(minutes=5), send_messages=True)

    @loader.command()
    async def kick(self, message: Message):
        """(reply) - Кикнуть пользователя"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings["no_reply"])
            return

        try:
            await self._client.kick_participant(message.chat_id, reply.sender_id)
            await utils.answer(
                message,
                self.strings["kicked"].format(
                    get_display_name(await self._client.get_entity(reply.sender_id))
                )
            )
        except:
            await utils.answer(message, self.strings["no_rights"])

    @loader.command()
    async def setstatus(self, message: Message):
        """<статус> (reply) - Установить статус"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        if not reply or not args or args.lower() not in self.statuses:
            await utils.answer(message, self.strings["no_reply"])
            return

        user = reply.sender_id
        self.users_status[user] = self.statuses[args.lower()]

        await utils.answer(
            message,
            self.strings["status_set"].format(
                self.statuses[args.lower()],
                get_display_name(await self._client.get_entity(user))
            )
        )

    @loader.command()
    async def stat(self, message: Message):
        """(reply) - Показать статистику"""
        reply = await message.get_reply_message()
        user = message.sender_id if not reply else reply.sender_id

        entity = await self._client.get_entity(user)
        status = self.users_status.get(user, "Нет статуса")

        text = (
            "📊 <b>{} статистика:</b>\n\n"
            "👤 <b>Имя:</b> {}\n"
            "🆔 <b>ID:</b> {}\n"
            "⭐ <b>Статус:</b> {}\n"
            "📅 <b>Дата регистрации:</b> {}"
        ).format(
            "Твоя" if user == message.sender_id else "Пользователя",
            get_display_name(entity),
            user,
            status,
            entity.date.strftime("%d.%m.%Y") if hasattr(entity, "date") else "Неизвестно"
        )

        await utils.answer(message, text)

    async def _mod_action(self, message, action, delta, **kwargs):
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings["no_reply"])
            return

        try:
            await self._client(
                EditBannedRequest(
                    message.chat_id,
                    reply.sender_id,
                    ChatBannedRights(
                        until_date=datetime.now() + delta,
                        **kwargs
                    )
                )
            )
            await utils.answer(
                message,
                self.strings[action].format(
                    get_display_name(await self._client.get_entity(reply.sender_id))
                )
            )
        except:
            await utils.answer(message, self.strings["no_rights"])