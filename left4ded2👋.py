import random
from hikkatl.types import Message
from .. import loader, utils
import requests
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

@loader.tds
class Left4Dead2UltimateMod(loader.Module):
    """Полноценный модуль по Left 4 Dead 2 с расширенным функционалом"""
    strings = {
        "name": "L4D2Ultimate",
        "version": "1.2.1",
        "no_args": "❌ Укажи запрос: персонажи, оружие, перки, карты, спецзараженные, режимы, советы, рандом, версия, сервер, достижения",
        "error": "❌ Произошла ошибка при выполнении команды",
    }

    async def client_ready(self, client, db):
        self._client = client

    async def l4dcmd(self, message: Message):
        """Главная команда для получения информации о L4D2"""
        try:
            args = utils.get_args_raw(message)
            if not args:
                await utils.answer(message, self.strings("no_args"))
                return

            cmd = args.lower()
            
            if cmd == "оружие":
                await self.weapons_info(message)
            elif cmd == "персонажи":
                await self.characters_info(message)
            elif cmd == "спецзараженные":
                await self.specials_info(message)
            elif cmd == "карты":
                await self.campaigns_info(message)
            elif cmd == "перки":
                await self.perks_info(message)
            elif cmd == "режимы":
                await self.game_modes(message)
            elif cmd == "советы":
                await self.random_tip(message)
            elif cmd == "рандом":
                await self.random_info(message)
            elif cmd == "версия":
                await self.version_info(message)
            elif cmd == "сервер":
                await self.server_info(message)
            elif cmd == "достижения":
                await self.achievements_info(message)
            elif cmd == "помощь":
                await self.help_info(message)
            else:
                await utils.answer(message, "❌ Неизвестная команда. Используй .l4d помощь для списка команд")
        except Exception as e:
            logger.exception("Command failed")
            await utils.answer(message, f"{self.strings('error')}: {str(e)}")

    async def weapons_info(self, message: Message):
        """Информация об оружии"""
        text = (
            "🔫 <b>Оружие в Left 4 Dead 2 (v1.2.1):</b>\n\n"
            "<u>Основное оружие:</u>\n"
            "• Автоматы: M16A4, AK-47, SCAR-L, SG552\n"
            "• Дробовики: Pump Shotgun, Chrome Shotgun, SPAS-12, Auto Shotgun\n"
            "• Снайперские: Hunting Rifle, Military Sniper, AWP, Scout\n\n"
            "<u>Дополнительное оружие:</u>\n"
            "• Пистолеты: P220, Magnum\n"
            "• Гранаты: Molotov, Pipe Bomb, Bile Jar\n"
            "• Ближний бой: Кастет, Топор, Молоток, Котелок\n\n"
            "<i>Используй .l4d оружие_статы для подробных характеристик</i>"
        )
        await self.send_with_photo(message, text, "https://i.imgur.com/n8ZPfDL.jpeg")

    async def characters_info(self, message: Message):
        """Информация о персонажах"""
        text = (
            "👥 <b>Выжившие:</b>\n\n"
            "• <b>Коуч</b> - бывший тренер по футболу, любит поесть\n"
            "• <b>Эллис</b> - механик из Саванны, болтливый\n"
            "• <b>Ник</b> - азартный игрок, циничный\n"
            "• <b>Рошель</b> - репортер, решительная\n\n"
            "<i>У каждого персонажа уникальные диалоги и реакции</i>"
        )
        await self.send_with_photo(message, text, "https://i.imgur.com/vcrvSfX.jpeg")

    async def specials_info(self, message: Message):
        """Информация о спецзараженных"""
        text = (
            "🧟 <b>Спец-заражённые:</b>\n\n"
            "• <b>Охотник</b> - быстрые прыжки (15 урона за удар)\n"
            "• <b>Курильщик</b> - захватывает языком (20 урона/сек)\n"
            "• <b>Буммер</b> - привлекает орду рвотой\n"
            "• <b>Танк</b> - 6000 HP, кидает камни\n"
            "• <b>Ведьма</b> - мгновенно убивает если разозлить\n"
            "• <b>Заразитель</b> - ослепляет кислотой\n\n"
            "<i>Слушайте звуки для определения типа заражённого</i>"
        )
        await self.send_with_photo(message, text, "https://i.imgur.com/FfFTV2C.jpeg")

    async def campaigns_info(self, message: Message):
        """Информация о кампаниях"""
        text = (
            "🗺️ <b>Кампании:</b>\n\n"
            "1. <b>Мёртвый центр</b> (5 карт)\n"
            "2. <b>Тёмные углы</b> (5 карт)\n"
            "3. <b>Переполох на болотах</b> (5 карт)\n"
            "4. <b>Выживший</b> (1 карта)\n"
            "5. <b>Приход</b> (5 карт, дополнение)\n\n"
            "<i>Всего 28 карт в стандартной игре</i>"
        )
        await self.send_with_photo(message, text, "https://i.imgur.com/KIRNWtm.jpeg")

    async def perks_info(self, message: Message):
        """Информация о перках"""
        text = (
            "🌟 <b>Перки:</b>\n\n"
            "<u>Для выживших:</u>\n"
            "• Боевой дух: +25% скорость атаки\n"
            "• Химическая стойкость: -80% урон от кислоты\n"
            "• Тяжеловес: +50% отбрасывание врагов\n\n"
            "<u>Для заражённых:</u>\n"
            "• Скорость: +10% к скорости\n"
            "• Живучесть: +30% здоровье"
        )
        await self.safe_send(message, text)

    async def game_modes(self, message: Message):
        """Информация о режимах игры"""
        text = (
            "🎲 <b>Режимы игры:</b>\n\n"
            "• <b>Кампания</b> - прохождение карт по порядку\n"
            "• <b>Реализм</b> - нет подсветки, сложнее\n"
            "• <b>Выживание</b> - держаться как можно дольше\n"
            "• <b>Наперегонки</b> - соревнование между командами\n"
            "• <b>Мутации</b> - специальные модификации игры\n\n"
            "<i>Используй .l4d режим <название> для подробностей</i>"
        )
        await self.safe_send(message, text)

    async def random_tip(self, message: Message):
        """Случайный совет"""
        tips = [
            "💡 Всегда проверяйте углы перед движением вперед",
            "💡 Используйте гранаты для контроля толпы",
            "💡 В Реализме не стреляйте в союзников - урон полный",
            "💡 Ведьму можно убить снайперской винтовкой с одного выстрела в голову",
            "💡 Танка можно поджечь - он будет получать урон со временем"
        ]
        await self.safe_send(message, random.choice(tips))

    async def random_info(self, message: Message):
        """Случайная информация"""
        options = [
            self.weapons_info,
            self.characters_info,
            self.specials_info,
            self.campaigns_info,
            self.perks_info,
            self.game_modes,
            self.random_tip
        ]
        await random.choice(options)(message)

    async def version_info(self, message: Message):
        """Информация о версии"""
        text = (
            f"🛠️ <b>Left 4 Dead 2 (версия {self.strings('version')})</b>\n\n"
            "<i>Последние изменения:</i>\n"
            "• Баланс оружия\n"
            "• Исправление багов с Танком\n"
            "• Оптимизация сетевого кода\n\n"
            "<i>Дата выхода:</i> 17 ноября 2009 года"
        )
        await self.safe_send(message, text)

    async def server_info(self, message: Message):
        """Информация о серверах"""
        text = (
            "🖥️ <b>Серверная информация:</b>\n\n"
            "• Официальные сервера Valve\n"
            "• Поддержка пользовательских серверов\n"
            "• Режим Dedicated Server\n"
            "• Максимальное количество игроков: 8 (4vs4)\n\n"
            "<i>Пинг обычно составляет 30-100 мс</i>"
        )
        await self.safe_send(message, text)

    async def achievements_info(self, message: Message):
        """Информация о достижениях"""
        text = (
            "🏆 <b>Достижения:</b>\n\n"
            "• <b>Выживший</b> - пройти любую кампанию\n"
            "• <b>Неистовый стрелок</b> - убить 1000 зомби\n"
            "• <b>Дружественный огонь</b> - убить союзника\n"
            "• <b>Пироман</b> - поджечь 15 зомби одновременно\n\n"
            "<i>Всего 75 достижений в игре</i>"
        )
        await self.safe_send(message, text)

    async def help_info(self, message: Message):
        """Справка по командам"""
        text = (
            "🆘 <b>Доступные команды:</b>\n\n"
            "• <code>.l4d оружие</code> - всё оружие\n"
            "• <code>.l4d персонажи</code> - выжившие\n"
            "• <code>.l4d спецзараженные</code> - спец-заражённые\n"
            "• <code>.l4d карты</code> - кампании\n"
            "• <code>.l4d перки</code> - система перков\n"
            "• <code>.l4d режимы</code> - режимы игры\n"
            "• <code>.l4d советы</code> - случайный совет\n"
            "• <code>.l4d рандом</code> - случайная информация\n"
            "• <code>.l4d версия</code> - версия игры\n"
            "• <code>.l4d сервер</code> - серверная информация\n"
            "• <code>.l4d достижения</code> - достижения\n"
            "• <code>.l4d помощь</code> - эта справка\n\n"
            "<i>Версия модуля: 1.2.1</i>"
        )
        await self.safe_send(message, text)

    async def safe_send(self, message: Message, text: str):
        """Безопасная отправка текста"""
        try:
            await utils.answer(message, text)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            try:
                await message.delete()
                await self._client.send_message(message.peer_id, text)
            except Exception as e2:
                logger.error(f"Failed to send fallback message: {e2}")

    async def send_with_photo(self, message: Message, text: str, photo_url: str):
        """Улучшенная отправка фото"""
        try:
            # Сначала попробуем отправить как медиа
            photo = BytesIO(requests.get(photo_url).content)
            photo.name = "l4d2.jpg"
            
            await message.delete()
            await self._client.send_file(
                message.peer_id,
                photo,
                caption=text,
                force_document=False
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            try:
                # Fallback 1: Отправка текста с ссылкой на фото
                await self.safe_send(message, f"{text}\n\n📷 Фото: {photo_url}")
            except Exception as e2:
                logger.error(f"Failed to send fallback text: {e2}")
                try:
                    # Fallback 2: Просто текст
                    await self.safe_send(message, text)
                except Exception as e3:
                    logger.error(f"Failed to send plain text: {e3}")