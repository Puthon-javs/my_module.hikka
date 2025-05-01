from telethon import functions, types
from .. import loader, utils
import asyncio
import time
import requests
from io import BytesIO

@loader.tds
class FakeAccountDeleteMod(loader.Module):
    """Модуль для видимого удаления аккаунта (фейкового) с отчетом"""
    strings = {
        "name": "Fake Account Delete",
        "warning": "⚠️ Вы собираетесь видимо удалить свой аккаунт\n\nЭто сделает ваш профиль невидимым для других пользователей, но аккаунт останется\n\nДля подтверждения введите команду еще раз в течение 30 секунд\n\nДля отмены напишите .отмена",
        "processing": "🔹 Начинаю процесс видимого удаления аккаунта...",
        "cancelled": "❌ Видимое удаление отменено",
        "cancel_cmd": ".отмена",
        "error": "❌ Ошибка на шаге {}: {}",
        "success": "✅ Видимое удаление аккаунта успешно завершено!",
        "step_username": "🔹 Шаг 1/4: Удаление юзернейма...",
        "step_username_done": "   ✔️ Юзернейм успешно удален",
        "step_name": "🔹 Шаг 2/4: Изменение имени профиля...",
        "step_name_done": "   ✔️ Имя изменено на 'Deleted Account'",
        "step_photos": "🔹 Шаг 3/4: Удаление текущих фото профиля...",
        "step_photos_done": "   ✔️ Фото профиля удалены",
        "step_avatar": "🔹 Шаг 4/4: Установка стандартной аватарки...",
        "step_avatar_done": "   ✔️ Аватарка установлена",
    }

    def __init__(self):
        self.pending_deletions = {}
        self.default_avatar_url = "https://i.imgur.com/p5bczYy.jpeg"

    async def download_avatar(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(self.default_avatar_url, headers=headers, timeout=15)
            response.raise_for_status()
            if not response.headers.get('Content-Type', '').startswith('image/'):
                raise ValueError("URL не ведет на изображение")
            return BytesIO(response.content)
        except Exception as e:
            print(f"[FakeDelete] Ошибка загрузки аватарки: {e}")
            return None

    async def set_default_avatar(self, client):
        avatar_bytes = await self.download_avatar()
        if not avatar_bytes:
            return False
        try:
            avatar_bytes.seek(0)
            file = await client.upload_file(avatar_bytes)
            await client(functions.photos.UploadProfilePhotoRequest(file=file))
            return True
        except Exception as e:
            print(f"[FakeDelete] Ошибка установки аватарки: {e}")
            return False

    async def remove_username(self, client):
        try:
            await client(functions.account.UpdateUsernameRequest(username=""))
            return True
        except Exception as e:
            print(f"[FakeDelete] Ошибка удаления юзернейма: {e}")
            return False

    async def report_progress(self, message, text):
        """Отправляет отчет о прогрессе"""
        await utils.answer(message, text)
        await asyncio.sleep(1)  # Пауза для лучшей читаемости

    async def fakedeletecmd(self, message):
        user_id = message.sender_id
        current_time = time.time()

        if self.strings["cancel_cmd"].lower() in message.text.lower():
            if user_id in self.pending_deletions:
                del self.pending_deletions[user_id]
                await utils.answer(message, self.strings["cancelled"])
            return

        if user_id in self.pending_deletions and current_time - self.pending_deletions[user_id] < 30:
            await self.report_progress(message, self.strings["processing"])

            try:
                # Шаг 1: Удаление юзернейма
                await self.report_progress(message, self.strings["step_username"])
                if not await self.remove_username(message.client):
                    raise Exception("Не удалось удалить юзернейм")
                await self.report_progress(message, self.strings["step_username_done"])

                # Шаг 2: Изменение имени
                await self.report_progress(message, self.strings["step_name"])
                await message.client(functions.account.UpdateProfileRequest(
                    first_name="Deleted",
                    last_name="Account",
                    about="This account is no longer available"
                ))
                await self.report_progress(message, self.strings["step_name_done"])

                # Шаг 3: Удаление фото
                await self.report_progress(message, self.strings["step_photos"])
                photos = await message.client.get_profile_photos('me')
                if photos:
                    await message.client(functions.photos.DeletePhotosRequest(photos))
                await self.report_progress(message, self.strings["step_photos_done"])

                # Шаг 4: Установка аватарки
                await self.report_progress(message, self.strings["step_avatar"])
                if not await self.set_default_avatar(message.client):
                    raise Exception("Не удалось установить аватарку")
                await self.report_progress(message, self.strings["step_avatar_done"])

                # Финальное сообщение
                await utils.answer(message, self.strings["success"])

            except Exception as e:
                await utils.answer(message, self.strings["error"].format("выполнения операции", str(e)))
            finally:
                if user_id in self.pending_deletions:
                    del self.pending_deletions[user_id]
        else:
            self.pending_deletions[user_id] = current_time
            await utils.answer(message, self.strings["warning"])
            
            async def cleanup():
                await asyncio.sleep(30)
                if user_id in self.pending_deletions:
                    del self.pending_deletions[user_id]
            
            asyncio.create_task(cleanup())

    async def watcher(self, message):
        if not message.out:
            return
            
        if self.strings["cancel_cmd"].lower() in message.text.lower():
            user_id = message.sender_id
            if user_id in self.pending_deletions:
                del self.pending_deletions[user_id]
                await utils.answer(message, self.strings["cancelled"])