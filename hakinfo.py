from hikkatl.types import Message
from hikkatl.utils import get_display_name
from .. import loader, utils
import random
import time
from datetime import datetime

@loader.tds
class HackerInfoMod(loader.Module):
    """ получает информацию о хакере"""
    strings = {
        "name": "HackerInfo",
        "generating": "<b>Получаю информацию о хакере...</b>",
        "result": (
            "<b>╭─ ⋆⋅☆⋅⋆ ──── ⋆⋅☆⋅⋆ ──╮\n"
            "   ✦  Hacker Info ✦\n"
            "╰─ ⋆⋅☆⋅⋆ ──── ⋆⋅☆⋅⋆ ──╯</b>\n\n"
            "<b>🔍 IP Address:</b> <code>{ip}</code>\n"
            "<b>🌐 VPN:</b> {vpn}\n"
            "<b>🛡️ Proxy:</b> {proxy}\n"
            "<b>📍 Location:</b> {location}\n"
            "<b>💻 OS:</b> {os}\n"
            "<b>🕵️‍♂️ Hacker Name:</b> {hacker_name}\n"
            "<b>🔢 Ports Open:</b> {ports}\n"
            "<b>🚀 Last Attack:</b> {last_attack}\n"
            "<b>📊 Success Rate:</b> {success_rate}%\n\n"
            "<i>⚠️ Внимание: Это не игра.</i>"
        )
    }

    async def client_ready(self, client, db):
        self._client = client

    @loader.command(ru_doc="показать информацию о хакере")
    async def hacinfocmd(self, message: Message):
        """показать информацию о хакере"""
        await utils.answer(message, self.strings("generating"))
        
        # Генерация фейковых данных
        ip = f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
        
        vpns = [
            "NordVPN (Active) [Switzerland]",
            "ExpressVPN (Active) [Panama]",
            "CyberGhost (Inactive)",
            "Private Internet Access [USA]",
            "Tor over VPN [Germany]"
        ]
        
        proxies = [
            "Elite Proxy [Undetectable]",
            "Anonymous Proxy [Medium]",
            "Transparent Proxy [Detected]",
            "No Proxy [Direct Connection]",
            "Chain of 3 Proxies [Russia→Finland→Canada]"
        ]
        
        locations = [
            "Moscow, Russia (spoofed)",
            "Berlin, Germany (spoofed)",
            "Undisclosed Location [Onion Routing]",
            f"Area {random.randint(51, 53)} (Classified)",
            "The Dark Web [Tor Node]"
        ]
        
        os_versions = [
            "Kali Linux 2023.4",
            "Parrot OS 5.3",
            "Windows 11 Pro (VM)",
            "TAILS 5.12",
            "BlackArch Linux"
        ]
        
        hacker_names = [
            "PhantomLance",
            "ZeroCool",
            "Crash Override",
            "Acid Burn",
            f"x{random.randint(100, 999)}h4ck3r"
        ]
        
        # Исправление ошибки с преобразованием чисел в строки для ports
        ports = ", ".join(
            str(port) for port in sorted(
                random.sample(
                    [21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080],
                    random.randint(3, 6)
                )
            )
        )
        
        last_attack = datetime.fromtimestamp(
            time.time() - random.randint(60, 86400)
        ).strftime("%Y-%m-%d %H:%M:%S")
        
        result = self.strings("result").format(
            ip=ip,
            vpn=random.choice(vpns),
            proxy=random.choice(proxies),
            location=random.choice(locations),
            os=random.choice(os_versions),
            hacker_name=random.choice(hacker_names),
            ports=ports,
            last_attack=last_attack,
            success_rate=random.randint(65, 99)
        )
        
        await utils.answer(message, result)