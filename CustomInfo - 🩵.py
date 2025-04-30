from .. import loader, utils
import git
import platform
import psutil
import time
import os
from telethon.tl.types import MessageEntityUrl
import re

__version__ = (3, 0, 0)
# meta developer: @Python_Javs

@loader.tds
class CustomInfoMod(loader.Module):
    """Улучшенная информация о юзерботе - ping, и т.д."""

    strings = {
        "name": "Info ⛵", 
        "update_available": "<b>Доступно обновление!</b>",
        "latest_version": "<b>У вас последняя версия.</b>",
        "old_format_warning": "<b>🇦🇲 Тег {system_info} устарел. Используйте:\n\n{ram_using} - использованная RAM\n{ram_total} - всего RAM\n{rom_using} - использованная память\n{rom_total} - всего памяти</b>",
        "custom_format": (
            "<blockquote>🩷 Owner:users</blockquote>\n\n"
            "<blockquote>🩷 Version: 6.8.9\n"
            "🩷 Branch: {branch}\n"
            "🩷 Prefix: «-»</blockquote>\n\n"
            "<blockquote>🩷 Uptime: {uptime}\n"
            "🩷 CPU: {cpu_usage}%\n"
            "🩷 RAM: {ram_used} MB</blockquote>\n\n"
            "<blockquote>🩷 My modules: @Python_Javs\n"
            "🩷 Official developer</blockquote>"
        )
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            "custom_info_text",
            "<emoji document_id=5219899949281453881>🛠</emoji> <b>-[-INFORMATION-]-</b>\n\n"
            "<emoji document_id=5247213725080890199>⚜</emoji><b> Owner:</b> <b>{owner}</b>\n\n"
            "<emoji document_id=5219943216781995020>🚸</emoji> <b>Version:</b> <b>{version}</b>\n"
            "<emoji document_id=5222108309795908493>🌱</emoji><b>Branch:</b> <b>{branch}</b>\n"
            "<emoji document_id=5222148368955877900>🦋</emoji> <b>{update_status}</b>\n\n"
            "<emoji document_id=5453900977432188793>🦅</emoji> <b>Ping:</b> <b>{ping}</b> <b>мс</b>\n"
            "<emoji document_id=5258113901106580375>👑</emoji> <b>Аптайм:</b> <b>{uptime}</b>\n"
            "<emoji document_id=5258466217273871977>🧑‍💻</emoji> <b>Префикс:</b> «<b>{prefix}</b>»\n\n"
            "<emoji document_id=5873146865637133757>🌊</emoji> <b>RAM сервера:</b> <code>{ram_using} GB | {ram_total} GB</code>\n"
            "<emoji document_id=5870982283724328568>👾</emoji> <b>Память:</b> <code>{rom_using} GB | {rom_total} GB</code>\n\n"
            "<emoji document_id=5391034312759980875>🕷</emoji><b> OC: {os_name} {os_version}</b>\n"
            "<emoji document_id=5235588635885054955>🐾</emoji> <b>Процессор:</b> <b>{cpu_info}</b>",
            lambda: "Шаблон для вывода информации",
            
            "banner_url",
            "https://i.imgur.com/eLZMivm.jpeg",
            lambda: "URL баннера, который будет отправлен с информацией (None чтобы отключить)",
            
            "use_custom_format",
            False,
            lambda: "Использовать кастомный формат вывода"
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._client = client

    def get_cpu_info(self):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except:
            return platform.processor() or "Unknown"

    def get_cpu_usage(self):
        try:
            return psutil.cpu_percent(interval=1)
        except:
            return 0.0

    def get_ram_info(self):
        try:
            ram = psutil.virtual_memory()
            total = round(ram.total / (1024**3), 2)
            used = round(ram.used / (1024**3), 2)
            return used, total
        except:
            return 0, 0

    def get_ram_usage_mb(self):
        try:
            ram = psutil.virtual_memory()
            return round(ram.used / (1024**2), 1)
        except:
            return 0

    def get_disk_info(self):
        try:
            disk = psutil.disk_usage('/')
            total = round(disk.total / (1024**3), 2)
            used = round(disk.used / (1024**3), 2)
            return used, total
        except:
            return 0, 0
            
    @loader.command()
    async def pinfo(self, message):
        """Показать информацию о юзерботе"""
        try:
            repo = git.Repo(search_parent_directories=True)
            branch = repo.active_branch.name
            diff = repo.git.log([f"HEAD..origin/{branch}", "--oneline"])
            update_status = self.strings["update_available"] if diff else self.strings["latest_version"]
        except:
            branch = "unknown"
            update_status = "Невозможно проверить обновления"
            
        start = time.perf_counter_ns()
        msg = await message.client.send_message("me", '💜')
        ping = round((time.perf_counter_ns() - start) / 10**6, 3)
        await msg.delete()

        ram_used, ram_total = self.get_ram_info()
        ram_used_mb = self.get_ram_usage_mb()
        disk_used, disk_total = self.get_disk_info()
        cpu_usage = self.get_cpu_usage()

        if self.config["use_custom_format"]:
            template = self.strings["custom_format"]
            format_dict = {
                "branch": branch,
                "uptime": utils.formatted_uptime(),
                "cpu_usage": cpu_usage,
                "ram_used": ram_used_mb
            }
        else:
            template = self.config["custom_info_text"]
            format_dict = {
                "owner": self._client.hikka_me.first_name + ' ' + (self._client.hikka_me.last_name or ''),
                "version": '3.0.0',
                "branch": branch,
                "update_status": update_status,
                "prefix": self.get_prefix(),
                "ping": ping,
                "uptime": utils.formatted_uptime(),
                "ram_using": ram_used,
                "ram_total": ram_total,
                "rom_using": disk_used,
                "rom_total": disk_total,
                "os_name": platform.system(),
                "os_version": platform.release(),
                "cpu_info": self.get_cpu_info()
            }

            if "{system_info}" in template:
                format_dict["system_info"] = self.strings["old_format_warning"]

        info = template.format(**format_dict)
        
        reply_to = await message.get_reply_message()
        thread = getattr(message, 'message_thread_id', None)

        if self.config["banner_url"]:
            await self.client.send_file(
                message.peer_id,
                self.config["banner_url"],
                caption=info,
                reply_to=reply_to.id if reply_to else None,
                message_thread_id=thread
            )
            if message.out:
                await message.delete()
        else:
            await utils.answer(
                message,
                info
            )

    @loader.command()
    async def setcinfo(self, message):
        """Установить кастомный текст информации: .setcinfo <текст>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5314413943035278948>🔋</emoji><b> Укажите текст для кастомной информации!")
            return

        self.config["custom_info_text"] = args
        await utils.answer(message, "<emoji document_id=5314413943035278948>🔋</emoji><b> CustomInfo - текст поставлен.</b>")

    @loader.command()
    async def togglectm(self, message):
        """Переключить между кастомным и стандартным форматом"""
        self.config["use_custom_format"] = not self.config["use_custom_format"]
        status = "включен" if self.config["use_custom_format"] else "выключен"
        await utils.answer(message, f"<emoji document_id=5332533929020761310>✅</emoji> <b>Кастомный формат {status}</b>")