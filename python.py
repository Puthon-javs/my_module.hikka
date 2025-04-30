from hikkatl.types import Message
from hikkatl.errors import BadRequestError
from hikkapyro import filters
from hikkapyro.types import InlineKeyboardMarkup, InlineKeyboardButton
import io
import ast
import inspect
import re
from typing import Dict, List, Optional, Tuple

from .. import loader, utils


@loader.tds
class ScriptAnalyzerMod(loader.Module):
    """Анализатор Python скриптов - показывает содержимое, ошибки, None и проверяет безопасность"""

    strings = {
        "name": "ScriptAnalyzer",
        "no_file": "🚫 Файл не найден. Пожалуйста, ответьте на файл с Python скриптом.",
        "analysis": "📊 <b>Анализ скрипта:</b>\n\n{content}",
        "errors": "❌ <b>Ошибки синтаксиса:</b>\n{errors}",
        "none_values": "🔍 <b>Найдены None значения:</b>\n{nones}",
        "security": "🛡️ <b>Проверка безопасности:</b>\n{security}",
        "too_long": "📜 <b>Содержимое слишком длинное, отправляю как файл...</b>",
    }

    async def client_ready(self, client, db):
        self._client = client

    @staticmethod
    def _analyze_script(code: str) -> Dict[str, List[str]]:
        """Анализирует Python код и возвращает ошибки, None и проблемы безопасности"""
        result = {"errors": [], "nones": [], "security": []}
        
        # Проверка синтаксиса
        try:
            ast.parse(code)
        except SyntaxError as e:
            result["errors"].append(f"Строка {e.lineno}: {e.msg}")
        
        # Поиск None значений
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == "None":
                    result["nones"].append(f"Строка {node.lineno}: Найден None")
                elif isinstance(node, ast.Constant) and node.value is None:
                    result["nones"].append(f"Строка {node.lineno}: Найден None")
        except:
            pass
        
        # Проверка безопасности
        dangerous_patterns = [
            (r"exec\(", "Использование exec() может быть опасным"),
            (r"eval\(", "Использование eval() может быть опасным"),
            (r"__import__\(", "Прямой вызов __import__() может быть опасным"),
            (r"subprocess\.", "Использование subprocess может быть опасным"),
            (r"os\.system\(", "Использование os.system() может быть опасным"),
            (r"pickle\.loads\(", "Десериализация pickle может быть опасной"),
            (r"open\(", "Использование open() без проверки пути может быть опасным"),
            (r"\.write\(", "Операции записи в файл могут быть опасными"),
        ]
        
        for pattern, warning in dangerous_patterns:
            if re.search(pattern, code):
                result["security"].append(warning)
        
        return result

    async def _send_long_text(self, message: Message, text: str, filename: str = "analysis.txt"):
        """Отправляет длинный текст как файл"""
        file = io.BytesIO(text.encode("utf-8"))
        file.name = filename
        await message.reply(file=file)
        return

    @loader.unrestricted
    async def sazcmd(self, message: Message):
        """Анализировать Python скрипт - ответьте на файл с командой .saz"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await utils.answer(message, self.strings["no_file"])
            return

        try:
            file = await reply.download_media(bytes)
            code = file.decode("utf-8")
        except UnicodeDecodeError:
            await utils.answer(message, "❌ Файл не является текстовым Python скриптом")
            return
        except Exception as e:
            await utils.answer(message, f"❌ Ошибка при чтении файла: {str(e)}")
            return

        # Анализ скрипта
        analysis = self._analyze_script(code)
        
        # Формирование ответа
        parts = []
        
        # Содержимое скрипта
        content_msg = f"<code>{utils.escape_html(code[:2000])}</code>"
        if len(code) > 2000:
            content_msg += "\n\n..." + self.strings["too_long"]
            parts.append(self.strings["analysis"].format(content=content_msg))
            await utils.answer(message, "\n\n".join(parts))
            await self._send_long_text(message, code, "script.py")
        else:
            parts.append(self.strings["analysis"].format(content=content_msg))
        
        # Ошибки
        if analysis["errors"]:
            errors = "\n".join(f"• {e}" for e in analysis["errors"])
            parts.append(self.strings["errors"].format(errors=errors))
        else:
            parts.append("✅ <b>Ошибок синтаксиса не найдено</b>")
        
        # None значения
        if analysis["nones"]:
            nones = "\n".join(f"• {n}" for n in analysis["nones"])
            parts.append(self.strings["none_values"].format(nones=nones))
        else:
            parts.append("✅ <b>None значений не найдено</b>")
        
        # Проблемы безопасности
        if analysis["security"]:
            security = "\n".join(f"• {s}" for s in analysis["security"])
            parts.append(self.strings["security"].format(security=security))
        else:
            parts.append("✅ <b>Опасных конструкций не найдено</b>")
        
        # Отправка результата
        full_message = "\n\n".join(parts)
        if len(full_message) > 4096:
            await utils.answer(message, self.strings["too_long"])
            await self._send_long_text(message, full_message)
        else:
            await utils.answer(message, full_message)