# Proprietary License Agreement

# Copyright (c) 2024-29 CodWiz

# Permission is hereby granted... [остальная часть лицензии остается без изменений]

# ---------------------------------------------------------------------------------
# Name: SpamBan 🚫
# Description: Check spam ban for your account.
# Author: @ManagerMatrix
# ---------------------------------------------------------------------------------
# meta developer: @Python_Javs
# scope: CheckSpamBan
# scope: CheckSpamBan 0.0.1
# ---------------------------------------------------------------------------------

from .. import loader, utils
from ..utils import answer
from telethon.tl.types import Message

__version__ = (1, 0, 1)  # Увеличил версию

@loader.tds
class SpamBanCheckMod(loader.Module):
    """Check spam ban for your account."""

    strings = {
        "name": "SpamBan 🚫",
        "svo": "Ваш аккаунт свободен от каких-либо ограничений.",
        "good": "<b>✅ Все хорошо! У вас нет спам-бана можете ити дальше спамить.</b>",
        "spamban": "<b>⚠️ Обнаружен спам-бан! не повезло тебе \n\nПричина: {reason}\nРешение: {solution}</b>",
        "unknown": "<b>❓ Неизвестный ответ от SpamBot:\n\n{response}</b>",
        "error": "<b>❌ Ошибка проверки спам-бана: {error}</b>"
    }

    @loader.command(
        ru_doc="Проверяет вашу учетную запись на спам-бан с помощью бота @SpamBot",
        en_doc="Checks your account for spam ban via @SpamBot bot",
    )
    async def spambancmd(self, message: Message):
        """Check spam ban status"""
        try:
            async with self._client.conversation("@SpamBot") as conv:
                msg = await conv.send_message("/start")
                r = await conv.get_response()
                
                if r.text == self.strings("svo"):
                    text = self.strings("good")
                else:
                    response_lines = [line.strip() for line in r.text.split("\n") if line.strip()]
                    
                    # Более гибкий парсинг ответа
                    reason = "Not specified"
                    solution = "Contact @SpamBot for details"
                    
                    # Ищем строки, которые могут содержать причину и решение
                    for i, line in enumerate(response_lines):
                        if "reason" in line.lower() or "причина" in line.lower():
                            reason = line
                            if i+1 < len(response_lines):
                                reason += "\n" + response_lines[i+1]
                        elif "solution" in line.lower() or "решение" in line.lower():
                            solution = line
                            if i+1 < len(response_lines):
                                solution += "\n" + response_lines[i+1]
                    
                    if len(response_lines) > 1:
                        text = self.strings("spamban").format(reason=reason, solution=solution)
                    else:
                        text = self.strings("unknown").format(response=r.text)
                
                await msg.delete()
                await r.delete()
                await answer(message, text)
                
        except Exception as e:
            await answer(message, self.strings("error").format(error=str(e)))