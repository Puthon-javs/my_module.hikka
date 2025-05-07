from hikkatl.types import Message
from hikkatl.utils import get_display_name
from .. import loader, utils
import random
import asyncio

class LoveAnimationMod(loader.Module):
    """Разнотупные анимации любви с сердечками"""
    
    strings = {
        "name": "LoveAnim",
        "loading": "💖 Готовлю анимацию...",
        "no_reply": "❌ Ответь на сообщение, чтобы послать любовь!",
    }

    def __init__(self):
        self.animations = [
            self.heart_explosion,
            self.flying_hearts,
            self.heart_rain,
            self.heart_spiral,
            self.heart_wave,
            self.heart_arrow,
            self.heart_burst,
            self.heart_galaxy,
        ]
        self.emoji_sets = {
            "classic": ["❤", "🧡", "💛", "💚", "💙", "💜"],
            "hearts": ["💘", "💝", "💖", "💗", "💓", "💞", "💕"],
            "sparks": ["✨", "🌟", "⭐", "💫", "☄", "🌠"],
            "fire": ["🔥", "🎇", "🎆", "🌋", "💥"],
            "nature": ["🌹", "🌸", "🌺", "🌻", "🍀", "🌷"],
            "random": ["❤", "☀", "⚡", "🌙", "🌈", "🌊", "🍎", "🎯"],
        }

    async def client_ready(self, client, db):
        self._client = client

    @loader.command()
    async def love(self, message: Message):
        """Запустить анимацию любви"""
        reply = await message.get_reply_message()
        
        if not reply:
            await utils.answer(message, self.strings["no_reply"])
            return
            
        await utils.answer(message, self.strings["loading"])
        
        # Выбираем случайную анимацию и набор эмодзи
        anim = random.choice(self.animations)
        emoji_set = random.choice(list(self.emoji_sets.values()))
        
        # Запускаем анимацию
        await anim(message, reply, emoji_set)
        
    async def heart_explosion(self, message: Message, reply: Message, emojis: list):
        """Анимация взрыва сердечек"""
        text = " ".join([random.choice(emojis) for _ in range(20)])
        center = await reply.reply("💥")
        
        for _ in range(10):
            new_text = " ".join([random.choice(emojis) for _ in range(30)])
            await asyncio.sleep(0.3)
            await center.edit(new_text)
            
        sender = await self._client.get_entity(reply.sender_id)
        await center.edit(f"💖 {get_display_name(sender)} 💖\n" + 
                         "ТЫ ПРОСТО КОСМОС! 🌟")
        
    async def flying_hearts(self, message: Message, reply: Message, emojis: list):
        """Летающие сердечки"""
        msg = await reply.reply("✈")
        
        for i in range(1, 15):
            await asyncio.sleep(0.2)
            heart = random.choice(emojis)
            await msg.edit(" " * i + heart)
            
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"{random.choice(emojis)} {get_display_name(sender)} " + 
                      f"{random.choice(emojis)}\nЛЮБЛЮ ТЕБЯ! {random.choice(emojis)*3}")
        
    async def heart_rain(self, message: Message, reply: Message, emojis: list):
        """Дождь из сердечек"""
        msg = await reply.reply("☁")
        
        for _ in range(5):
            for line in range(1, 6):
                rain = "\n".join([" ".join([random.choice(emojis) for _ in range(5)]) 
                          for _ in range(line)])
                await msg.edit(rain)
                await asyncio.sleep(0.3)
                
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"🌧 Дождь любви для {get_display_name(sender)}!\n" + 
                      "".join(random.choice(emojis) for _ in range(10)))
        
    async def heart_spiral(self, message: Message, reply: Message, emojis: list):
        """Спираль из сердечек"""
        spiral = ["◜", "◝", "◞", "◟"]
        msg = await reply.reply("🌀")
        
        for _ in range(3):
            for direction in spiral:
                await msg.edit(direction + random.choice(emojis))
                await asyncio.sleep(0.2)
                
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"🌀 Любовная спираль к {get_display_name(sender)}!\n" + 
                      "".join(random.choice(emojis) for _ in range(10)))
        
    async def heart_wave(self, message: Message, reply: Message, emojis: list):
        """Волна из сердечек"""
        msg = await reply.reply("🌊")
        wave = ["~" * i + random.choice(emojis) for i in range(1, 6)]
        
        for _ in range(5):
            for w in wave:
                await msg.edit(w)
                await asyncio.sleep(0.2)
                
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"🌊 Волна любви накрыла {get_display_name(sender)}!\n" + 
                      "".join(random.choice(emojis) for _ in range(10)))
        
    async def heart_arrow(self, message: Message, reply: Message, emojis: list):
        """Стрела любви"""
        msg = await reply.reply("🏹")
        
        for i in range(1, 10):
            await msg.edit("~" * i + "💘")
            await asyncio.sleep(0.1)
            
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"💘 {get_display_name(sender)}, ты поражен(а) любовью!\n" + 
                      "".join(random.choice(emojis) for _ in range(10)))
        
    async def heart_burst(self, message: Message, reply: Message, emojis: list):
        """Взрыв любви"""
        msg = await reply.reply("💣")
        
        for size in ["small", "medium", "big"]:
            if size == "small":
                burst = "💥 " + " ".join([random.choice(emojis) for _ in range(5)])
            elif size == "medium":
                burst = "💥 " + " ".join([random.choice(emojis) for _ in range(10)])
            else:
                burst = "💥 " + " ".join([random.choice(emojis) for _ in range(20)])
                
            await msg.edit(burst)
            await asyncio.sleep(0.5)
            
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"💖 {get_display_name(sender)} взорван(а) любовью!\n" + 
                      "".join([random.choice(emojis) for _ in range(15)]))
        
    async def heart_galaxy(self, message: Message, reply: Message, emojis: list):
        """Галактика любви"""
        msg = await reply.reply("🌌")
        space = ["🌠", "🌟", "⭐", "☄", "💫", "✨"]
        
        for _ in range(10):
            galaxy = " ".join([random.choice(space + emojis) for _ in range(15)])
            await msg.edit(galaxy)
            await asyncio.sleep(0.3)
            
        sender = await self._client.get_entity(reply.sender_id)
        await msg.edit(f"🌌 Галактика любви для {get_display_name(sender)}!\n" + 
                      "".join([random.choice(emojis + space) for _ in range(20)]))
