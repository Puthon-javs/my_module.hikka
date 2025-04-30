# meta developer: @Python_Javs


from hikkatl.types import Message
from hikkatl.utils import get_display_name
from .. import loader, utils
import random
import asyncio

@loader.tds
class ValentinesModule(loader.Module):
    """Модуль для отправки валентинок"""

    strings = {
        "name": "Valentines",
        "no_reply": "🚫 <b>Нужно ответить на сообщение пользователя!</b>",
        "valentine_sent": "💌 <b>Валентинка отправлена!</b>",
        "ask_text": "✏️ <b>Напиши текст валентинки...</b>",
        "processing": "⏳ <b>Создаю валентинку...</b>",
    }

    strings_ru = {
        "no_reply": "🚫 <b>Нужно ответить на сообщение пользователя!</b>",
        "valentine_sent": "💌 <b>Валентинка отправлена!</b>",
        "ask_text": "✏️ <b>Напиши текст валентинки...</b>",
        "processing": "⏳ <b>Создаю валентинку...</b>",
    }

    async def valentinecmd(self, message: Message):
        """Отправить валентинку. Используй: .valentine <текст> или reply."""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("ask_text"))
            return

        user = await message.client.get_entity(reply.sender_id)
        name = get_display_name(user)
        me = await message.client.get_me()
        my_name = get_display_name(me)

        processing_msg = await utils.answer(message, self.strings("processing"))
        
        # Анимация отправки с проверкой на изменение
        hearts = ["❤️", "💖", "💗", "💓", "💞", "💕", "💘"]
        last_text = ""
        
        for _ in range(5):
            heart = random.choice(hearts)
            new_text = f"{heart} <b>Создаю валентинку...</b>"
            
            if new_text != last_text:
                try:
                    await processing_msg.edit(new_text)
                    last_text = new_text
                except:
                    pass
                
            await asyncio.sleep(0.5)

        # Создаем красивую валентинку
        valentine = f"""
💌 <b>Валентинка от {my_name}</b> 💌

{args}

✨ <i>Для {name}</i> ✨
        """.strip()

        await message.client.send_message(
            message.chat_id,
            valentine,
            reply_to=reply.id
        )
        
        try:
            await processing_msg.delete()
        except:
            pass