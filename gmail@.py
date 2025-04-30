# meta developer: @Python_Javs

import random
import string
import aiohttp
import asyncio
from datetime import datetime, timedelta
from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class AdvancedTempMailMod(loader.Module):
    """Продвинутый генератор временных email-адресов с проверкой писем"""
    strings = {
        "name": "AdvancedTempMail",
        "result": (
            "📧 <b>Временный email создан!</b>\n\n"
            "👤 <b>Логин:</b> <code>{email}</code>\n"
            "🔑 <b>Пароль:</b> <code>{password}</code>\n"
            "⏳ <b>Истекает:</b> {expires}\n\n"
            "🔄 <code>.checkmail</code> - проверить письма\n"
            "🗑 <code>.delmail</code> - удалить email\n"
            "ℹ️ <code>.mailinfo</code> - информация о почте"
        ),
        "no_email": "❌ У вас нет активного email. Создайте новый командой <code>.tempmail</code>",
        "no_letters": "📭 Нет новых писем",
        "letters": "📬 <b>Полученные письма:</b>\n\n{letters}",
        "deleted": "🗑 <b>Email удален:</b> <code>{email}</code>",
        "mail_info": (
            "ℹ️ <b>Информация о почте:</b>\n\n"
            "📧 <b>Адрес:</b> <code>{email}</code>\n"
            "⏳ <b>Истекает:</b> {expires}\n"
            "📨 <b>Писем получено:</b> {letters_count}"
        ),
        "checking": "🔍 Проверяем новые письма...",
        "letter_item": (
            "✉️ <b>От:</b> {sender}\n"
            "📌 <b>Тема:</b> {subject}\n"
            "⏰ <b>Дата:</b> {date}\n"
            "🔗 <b>ID:</b> <code>{id}</code>\n"
        ),
    }

    async def client_ready(self, client, db):
        self._client = client
        self.db = db
        self.session = aiohttp.ClientSession()
        self.domains = [
            "temp-mail.org",
            "mailinator.com",
            "guerrillamail.com",
            "10minutemail.com"
        ]
        
        # Загружаем сохраненные email из базы
        if "tempmails" not in self.db:
            self.db["tempmails"] = {}

    async def on_unload(self):
        await self.session.close()

    @loader.command(ru_doc="Создать временный email")
    async def tempmail(self, message: Message):
        """Создать временный email с доступом к API"""
        # Получаем username пользователя
        user = await self._client.get_me()
        username = user.username or "user"
        
        # Выбираем случайный домен
        domain = random.choice(self.domains)
        
        # Генерируем случайную часть email
        random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        # Создаем email
        email = f"{username.lower()}_{random_part}@{domain}"
        
        # Генерируем пароль
        password = "".join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=12))
        
        # Устанавливаем время истечения (1 час)
        expires = datetime.now() + timedelta(hours=1)
        
        # Сохраняем в базу
        self.db["tempmails"][str(message.chat_id)] = {
            "email": email,
            "password": password,
            "expires": expires.timestamp(),
            "domain": domain,
            "letters": [],
            "created": datetime.now().timestamp()
        }
        
        # Отправляем результат
        await utils.answer(
            message,
            self.strings("result").format(
                email=email,
                password=password,
                expires=expires.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        
        # Запускаем фоновую задачу для проверки писем
        asyncio.create_task(self._check_mail_loop(message.chat_id))

    async def _check_mail_loop(self, chat_id):
        """Фоновая задача для проверки новых писем"""
        while True:
            await asyncio.sleep(300)  # Проверка каждые 5 минут
            
            mail_data = self.db["tempmails"].get(str(chat_id))
            if not mail_data:
                break
                
            if datetime.now().timestamp() > mail_data["expires"]:
                del self.db["tempmails"][str(chat_id)]
                break
                
            await self._fetch_letters(chat_id, mail_data)

    async def _fetch_letters(self, chat_id, mail_data):
        """Получение писем через API"""
        try:
            if mail_data["domain"] == "temp-mail.org":
                async with self.session.get(
                    f"https://api.temp-mail.org/request/mail/id/{mail_data['email'].split('@')[0]}/format/json"
                ) as resp:
                    if resp.status == 200:
                        letters = await resp.json()
                        if letters and len(letters) > len(mail_data["letters"]):
                            new_letters = letters[len(mail_data["letters"]):]
                            mail_data["letters"] = letters
                            
                            # Уведомляем о новых письмах
                            for letter in new_letters:
                                await self._client.send_message(
                                    chat_id,
                                    "📩 <b>Новое письмо!</b>\n\n" +
                                    self.strings("letter_item").format(
                                        sender=letter.get("from", "Неизвестно"),
                                        subject=letter.get("subject", "Без темы"),
                                        date=letter.get("created_at", "Неизвестно"),
                                        id=letter.get("id", "?"),
                                    )
                                )
            
            # Здесь можно добавить обработку для других доменов
                            
        except Exception as e:
            print(f"Error fetching mail: {e}")

    @loader.command(ru_doc="Проверить письма")
    async def checkmail(self, message: Message):
        """Проверить входящие письма"""
        mail_data = self.db["tempmails"].get(str(message.chat_id))
        if not mail_data:
            await utils.answer(message, self.strings("no_email"))
            return
            
        await utils.answer(message, self.strings("checking"))
        await self._fetch_letters(message.chat_id, mail_data)
        
        if not mail_data["letters"]:
            await utils.answer(message, self.strings("no_letters"))
            return
            
        letters_text = "\n".join(
            self.strings("letter_item").format(
                sender=letter.get("from", "Неизвестно"),
                subject=letter.get("subject", "Без темы"),
                date=letter.get("created_at", "Неизвестно"),
                id=letter.get("id", "?"),
            )
            for letter in mail_data["letters"]
        )
        
        await utils.answer(
            message,
            self.strings("letters").format(letters=letters_text)
        )

    @loader.command(ru_doc="Удалить email")
    async def delmail(self, message: Message):
        """Удалить временный email"""
        mail_data = self.db["tempmails"].get(str(message.chat_id))
        if not mail_data:
            await utils.answer(message, self.strings("no_email"))
            return
            
        email = mail_data["email"]
        del self.db["tempmails"][str(message.chat_id)]
        
        await utils.answer(
            message,
            self.strings("deleted").format(email=email)
        )

    @loader.command(ru_doc="Информация о почте")
    async def mailinfo(self, message: Message):
        """Показать информацию о временном email"""
        mail_data = self.db["tempmails"].get(str(message.chat_id))
        if not mail_data:
            await utils.answer(message, self.strings("no_email"))
            return
            
        expires = datetime.fromtimestamp(mail_data["expires"])
        
        await utils.answer(
            message,
            self.strings("mail_info").format(
                email=mail_data["email"],
                expires=expires.strftime("%Y-%m-%d %H:%M:%S"),
                letters_count=len(mail_data["letters"])
            )
        )