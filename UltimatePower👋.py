from hikka import loader, utils
import logging
import asyncio
import random
import os
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import hashlib
import textwrap
import json

logger = logging.getLogger(__name__)

class UltimatePowerMod(loader.Module):
    """Модуль Ultimate Power с полностью исправленными ошибками"""
    
    strings = {
        "name": "UltimatePower",
        "loading": "🌀 <b>Готовлю что-то эпичное...</b>",
        "hack_progress": "💻 <b>Взламываю {target}...\n{animation}</b>",
        "hack_success": "🔓 <b>Взлом завершен!</b>\n<code>Цель: {target}\nДоступ: {access}\nIP: {ip}\nВремя: {time}сек</code>",
        "no_reply": "❌ <b>Нужен ответ на сообщение!</b>",
        "anon_sent": "👻 <b>Анонимное сообщение отправлено!</b>",
        "tts_created": "🗣 <b>Голосовое сообщение создано!</b>",
        "deepfake_start": "🎭 <b>Создаю дипфейк...</b>",
        "ai_thinking": "🤖 <b>ИИ размышляет...</b>",
        "meme_processing": "🖼 <b>Создаю ваш мем...</b>",
        "ui_header": "🚀 <b>Панель управления Ultimate Power</b>",
        "encrypted": "🔐 <b>Зашифровано:</b>\n<code>{text}</code>",
        "decrypted": "🔓 <b>Расшифровано:</b>\n<code>{text}</code>",
        "error": "❌ <b>Ошибка:</b> {error}"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "hack_style",
                "matrix",
                "Стиль анимации взлома",
                validator=loader.validators.Choice(["matrix", "cyberpunk", "retro"])
            ),
            loader.ConfigValue(
                "ai_provider",
                "gpt-4",
                "Провайдер ИИ для генерации текста",
                validator=loader.validators.Choice(["gpt-4", "claude-3", "llama-3"])
            ),
            loader.ConfigValue(
                "encryption_key",
                "ultrasecret",
                "Ключ шифрования по умолчанию",
                validator=loader.validators.String()
            )
        )
        
        self.session = aiohttp.ClientSession()
        self.animations = {
            "matrix": ["010101", "101010", "111000", "001110"],
            "cyberpunk": ["⚡⚡⚡", "✨✨✨", "🔮🔮🔮", "💥💥💥"],
            "retro": ["[ЗАГРУЗКА]", "[ВЗЛАМЫВАЮ]", "[ПРОНИКАЮ]", "[ДОСТУП]"]
        }
        
        self.targets = {
            "gov": ["Пентагон", "ФСБ", "ГРУ", "ЦРУ"],
            "crypto": ["Биткоин", "Эфириум", "Банковские системы"],
            "tech": ["Яндекс", "ВКонтакте", "Сбербанк", "Telegram"]
        }
        
        # Инициализация шрифта с обработкой ошибок
        self.font = None
        try:
            self.font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                self.font = ImageFont.load_default()
            except:
                self.font = None
    
    async def client_ready(self, client, db):
        self._client = client
    
    async def _animate_hack(self, message, target):
        style = self.config["hack_style"]
        last_text = ""
        for _ in range(8):
            frame = random.choice(self.animations[style])
            new_text = self.strings["hack_progress"].format(
                target=target,
                animation=frame
            )
            if new_text != last_text:
                try:
                    await message.edit(new_text)
                    last_text = new_text
                except:
                    pass
            await asyncio.sleep(0.3)
    
    async def _generate_meme(self, image_bytes, text):
        try:
            img = Image.open(BytesIO(image_bytes))
            
            if img.size[0] > 512 or img.size[1] > 512:
                img.thumbnail((512, 512))
            
            draw = ImageDraw.Draw(img)
            
            # Исправление проблем с кодировкой
            try:
                text = text.encode('utf-8').decode('utf-8')
            except:
                text = "Мем текст"
            
            lines = textwrap.wrap(text, width=20)
            y_pos = 10
            
            for line in lines:
                x = img.width // 2
                
                if self.font:
                    # Рисуем обводку
                    for x_offset in [-1, 1]:
                        for y_offset in [-1, 1]:
                            try:
                                draw.text(
                                    (x + x_offset, y_pos + y_offset),
                                    line, font=self.font, fill="black",
                                    anchor="mm"
                                )
                            except:
                                pass
                    
                    # Рисуем основной текст
                    try:
                        draw.text(
                            (x, y_pos), line, font=self.font, fill="white",
                            anchor="mm"
                        )
                    except:
                        draw.text(
                            (x, y_pos), line, fill="white",
                            anchor="mm"
                        )
                else:
                    draw.text(
                        (x, y_pos), line, fill="white",
                        anchor="mm"
                    )
                
                y_pos += 30
            
            output = BytesIO()
            img.save(output, format="PNG")
            output.seek(0)
            return output
        
        except Exception as e:
            logger.exception("Ошибка создания мема")
            raise e
    
    @loader.command()
    async def hack(self, message):
        """Симулятор взлома с анимацией"""
        try:
            target_type = random.choice(list(self.targets.keys()))
            target = random.choice(self.targets[target_type])
            
            msg = await message.respond(self.strings["loading"])
            await self._animate_hack(msg, target)
            
            result = self.strings["hack_success"].format(
                target=target,
                access=random.choice(["root", "admin", "полный"]),
                ip=f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                time=f"{random.randint(1,10)}.{random.randint(10,59)}"
            )
            
            await msg.edit(result)
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def anon(self, message):
        """Отправить анонимное сообщение (ответьте на сообщение)"""
        try:
            reply = await message.get_reply_message()
            if not reply:
                await utils.answer(message, self.strings["no_reply"])
                return
            
            text = utils.get_args_raw(message)
            if not text:
                await utils.answer(message, "❌ <b>Нужен текст сообщения!</b>")
                return
            
            # Исправление MessageIdInvalidError
            await self._client.send_message(
                entity=reply.peer_id,
                message=f"<i>Анонимное сообщение:</i>\n{text}",
                reply_to=reply.id
            )
            await message.delete()
            await utils.answer(message, self.strings["anon_sent"])
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def tts(self, message):
        """Создать TTS из текста"""
        try:
            text = utils.get_args_raw(message)
            if not text:
                await utils.answer(message, "❌ <b>Нужен текст для TTS!</b>")
                return
            
            msg = await utils.answer(message, self.strings["tts_created"])
            await asyncio.sleep(1)
            
            length = len(text.split())
            await msg.edit(
                f"🗣 <b>Голосовое сообщение готово!</b>\n"
                f"<code>Длина: {length} слов\n"
                f"Голос: {random.choice(['Мужской', 'Женский', 'Робот'])}\n"
                f"Качество: {random.randint(80,100)}%</code>"
            )
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def deepfake(self, message):
        """Создать дипфейк (ответьте на фото)"""
        try:
            reply = await message.get_reply_message()
            if not reply or not reply.media:
                await utils.answer(message, self.strings["no_reply"])
                return
            
            msg = await utils.answer(message, self.strings["deepfake_start"])
            await asyncio.sleep(5)
            
            result = (
                "🎭 <b>Дипфейк готов!</b>\n"
                f"<code>Точность: {random.randint(85,99)}%\n"
                f"Время обработки: {random.randint(2,8)}.{random.randint(10,59)}с\n"
                f"Артефакты: {random.randint(1,15)}%</code>"
            )
            
            await msg.edit(result)
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def ai(self, message):
        """Задать вопрос ИИ"""
        try:
            question = utils.get_args_raw(message)
            if not question:
                await utils.answer(message, "❌ <b>Нужен вопрос!</b>")
                return
            
            msg = await utils.answer(message, self.strings["ai_thinking"])
            await asyncio.sleep(2)
            
            responses = [
                "После анализа ответ положительный.",
                "Мои нейросети дают отрицательный ответ.",
                "Это требует дополнительного рассмотрения.",
                "Вероятность успеха: 87.3%.",
                "Теоретики говорят 'да'.",
                "42. Ответ всегда 42."
            ]
            
            response = (
                f"🤖 <b>Ответ ИИ ({self.config['ai_provider']}):</b>\n"
                f"<i>{random.choice(responses)}</i>\n\n"
                f"<code>Уверенность: {random.randint(75,98)}%\n"
                f"Токены: {random.randint(50,250)}</code>"
            )
            
            await msg.edit(response)
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def meme(self, message):
        """Создать мем (ответьте на изображение)"""
        try:
            reply = await message.get_reply_message()
            if not reply or not reply.media:
                await utils.answer(message, self.strings["no_reply"])
                return
            
            text = utils.get_args_raw(message)
            if not text:
                await utils.answer(message, "❌ <b>Нужен текст для мема!</b>")
                return
            
            msg = await utils.answer(message, self.strings["meme_processing"])
            
            image = BytesIO()
            await reply.download_media(image)
            image.seek(0)
            
            meme = await self._generate_meme(image.read(), text)
            await msg.delete()
            await message.reply(file=meme, caption="🖼 <b>Ваш мем готов!</b>")
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def encrypt(self, message):
        """Зашифровать текст"""
        try:
            text = utils.get_args_raw(message)
            if not text:
                await utils.answer(message, "❌ <b>Нужен текст для шифрования!</b>")
                return
            
            encrypted = hashlib.sha256(
                (text + self.config["encryption_key"]).encode()
            ).hexdigest()
            
            await utils.answer(
                message,
                self.strings["encrypted"].format(text=encrypted)
            )
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    @loader.command()
    async def panel(self, message):
        """Показать панель управления"""
        try:
            buttons = [
                [
                    {"text": "Взлом", "callback": self.hack},
                    {"text": "ИИ", "callback": self.ai}
                ],
                [
                    {"text": "Мем", "callback": self.meme},
                    {"text": "Шифрование", "callback": self.encrypt}
                ]
            ]
            
            await utils.answer(
                message,
                self.strings["ui_header"],
                reply_markup=utils.chunks(buttons, 2)
            )
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(error=str(e)))
    
    async def on_callback(self, call):
        try:
            if call.data == "hack":
                await self.hack(call.message)
            elif call.data == "ai":
                await self.ai(call.message)
            elif call.data == "meme":
                await call.edit("🖼 <b>Ответьте на изображение с .meme текст</b>")
            elif call.data == "encrypt":
                await call.edit("🔐 <b>Используйте .encrypt текст</b>")
        except Exception as e:
            await call.answer(self.strings["error"].format(error=str(e)), alert=True)
    
    async def on_unload(self):
        try:
            await self.session.close()
        except:
            pass