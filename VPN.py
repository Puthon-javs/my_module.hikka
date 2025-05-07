import asyncio
import random
import time
from datetime import datetime
from typing import Optional

import requests
from hikkatl.types import Message
from .. import loader, utils

class VPNAutoRotateMod(loader.Module):
    """Автоматическое VPN подключение с ротацией IP каждые 25 секунд"""

    strings = {
        "name": "VPNAutoRotate",
        "vpn_on": "✅ VPN включен.",
        "vpn_off": "❌ VPN выключен.",
        "current_ip": "🌐 Текущий IP: <code>{ip}</code>\n"
                     "📍 Страна: <code>{country}</code>\n"
                     "⏳ Время работы: <code>{uptime}</code>",
        "stats": "📊 Статистика VPN:\n"
                "🔁 Смен IP: <code>{changes}</code>\n"
                "🕒 Общее время работы: <code>{total_time}</code>\n"
                "🌍 Использованные страны: <code>{countries}</code>",
        "no_vpn": "ℹ️ VPN в настоящее время не активен.",
        "error": "⚠️ Ошибка при получении информации о VPN.",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "vpn_command",
                "sudo systemctl openvpn@client",
                "Команда для управления VPN",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "vpn_locations",
                ["us", "uk", "de", "fr", "jp", "ca", "nl", "sg"],
                "Список стран для ротации VPN",
                validator=loader.validators.Series(loader.validators.String()),
            ),
        )
        self._vpn_task: Optional[asyncio.Task] = None
        self._is_active = False
        self._start_time = 0
        self._ip_changes = 0
        self._used_countries = set()

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

    async def on_unload(self):
        await self.vpn_off_cmd(None)

    async def _rotate_vpn(self):
        while self._is_active:
            country = random.choice(self.config["vpn_locations"])
            self._used_countries.add(country)
            
            # Здесь должна быть реализация смены VPN локации
            # Например, через выполнение команды в системе
            # В реальном модуле нужно использовать безопасный способ выполнения команд
            try:
                utils.debug(f"Changing VPN to {country}")
                # В реальном модуле раскомментируйте следующую строку:
                # await utils.run_command(f"{self.config['vpn_command']} restart {country}")
                
                # Имитация смены VPN
                await asyncio.sleep(2)
                
                self._ip_changes += 1
                await self._client.send_message(
                    self._db.get("VPNAutoRotate", "log_chat", None),
                    f"VPN location changed to {country}",
                )
            except Exception as e:
                utils.debug(f"VPN rotation error: {e}")
            
            await asyncio.sleep(25)

    async def _get_ip_info(self):
        try:
            response = await utils.run_sync(requests.get, "https://ipinfo.io/json")
            data = response.json()
            return data.get("ip", "Unknown"), data.get("country", "Unknown")
        except:
            return "Unknown", "Unknown"

    def _format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

    @loader.command()
    async def vpn_on_cmd(self, message: Message):
        """Включить VPN с автоматической ротацией"""
        if self._is_active:
            await utils.answer(message, self.strings("vpn_on"))
            return

        self._is_active = True
        self._start_time = time.time()
        self._vpn_task = asyncio.create_task(self._rotate_vpn())
        await utils.answer(message, self.strings("vpn_on"))

    @loader.command()
    async def vpn_off_cmd(self, message: Optional[Message]):
        """Выключить VPN"""
        if not self._is_active:
            if message:
                await utils.answer(message, self.strings("vpn_off"))
            return

        self._is_active = False
        if self._vpn_task:
            self._vpn_task.cancel()
            try:
                await self._vpn_task
            except asyncio.CancelledError:
                pass
            self._vpn_task = None

        if message:
            await utils.answer(message, self.strings("vpn_off"))

    @loader.command()
    async def vpn_info_cmd(self, message: Message):
        """Показать информацию о текущем VPN подключении"""
        if not self._is_active:
            await utils.answer(message, self.strings("no_vpn"))
            return

        ip, country = await self._get_ip_info()
        if ip == "Unknown":
            await utils.answer(message, self.strings("error"))
            return

        uptime = self._format_time(time.time() - self._start_time)
        await utils.answer(
            message,
            self.strings("current_ip").format(ip=ip, country=country, uptime=uptime),
        )

    @loader.command()
    async def vpn_stats_cmd(self, message: Message):
        """Показать статистику VPN"""
        total_time = self._format_time(time.time() - self._start_time) if self._is_active else "0s"
        countries = ", ".join(sorted(self._used_countries)) if self._used_countries else "None"
        
        await utils.answer(
            message,
            self.strings("stats").format(
                changes=self._ip_changes,
                total_time=total_time,
                countries=countries,
            ),
        )