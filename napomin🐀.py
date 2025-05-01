from hikkatl.types import Message
from .. import loader, utils
from datetime import datetime, timedelta
import re
import asyncio

@loader.tds
class QuickReminderMod(loader.Module):
    """Устанавливай напоминания с уведомлениями"""
    strings = {
        "name": "QuickReminder",
        "reminder_set": "⏰ <b>Напоминание установлено!</b>\n<b>Текст:</b> <i>{}</i>\n<b>Когда:</b> <code>{}</code>",
        "invalid_time": "❌ <b>Неверный формат времени!</b>\nПримеры: <code>через 5 минут</code>, <code>завтра в 15:00</code>",
        "no_text": "❌ <b>Укажите текст напоминания!</b>",
        "reminder_list": "📋 <b>Активные напоминания:</b>\n\n{}",
        "no_reminders": "📭 <b>Нет активных напоминаний.</b>",
        "reminder_deleted": "🗑 <b>Напоминание удалено!</b> (ID: <code>{}</code>)",
        "not_found": "🔍 <b>Напоминание не найдено!</b>",
        "reminder_notify": "🔔 <b>Напоминание!</b>\n\n<i>{}</i>",
    }

    def __init__(self):
        self.reminders = {}
        self.reminder_id = 0

    async def _parse_time(self, time_str: str) -> datetime | None:
        time_str = time_str.lower()
        now = datetime.now()

        # "Через 5 минут"
        if "через" in time_str:
            nums = re.findall(r"\d+", time_str)
            if not nums:
                return None
            mins = int(nums[0])
            return now + timedelta(minutes=mins)

        # "Завтра в 15:00"
        if "завтра" in time_str:
            time_part = re.search(r"в (\d{1,2}):?(\d{2})?", time_str)
            if not time_part:
                return now + timedelta(days=1)
            hour = int(time_part.group(1))
            minute = int(time_part.group(2)) if time_part.group(2) else 0
            return (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0)

        # "31.12 в 23:59"
        date_match = re.search(r"(\d{1,2})\.(\d{1,2})(?: в (\d{1,2}):?(\d{2})?)?", time_str)
        if date_match:
            day = int(date_match.group(1))
            month = int(date_match.group(2))
            hour = int(date_match.group(3)) if date_match.group(3) else 12
            minute = int(date_match.group(4)) if date_match.group(4) else 0
            year = now.year if (month >= now.month and day >= now.day) else now.year + 1
            try:
                return datetime(year, month, day, hour, minute)
            except ValueError:
                return None

        return None

    async def _check_reminders(self):
        while True:
            now = datetime.now()
            to_delete = []
            for id_, (text, time) in self.reminders.items():
                if now >= time:
                    await self._notify_reminder(text)
                    to_delete.append(id_)
            for id_ in to_delete:
                del self.reminders[id_]
            await asyncio.sleep(10)

    async def _notify_reminder(self, text: str):
        await self.client.send_message(
            "me",
            self.strings["reminder_notify"].format(text),
        )

    async def client_ready(self, client, db):
        self.client = client
        asyncio.create_task(self._check_reminders())

    @loader.command(alias="remind")
    async def reminderaddcmd(self, message: Message):
        """Добавить напоминание. Пример: .remind через 30 минут купить хлеб"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_text"])
            return

        time_part = args.split(maxsplit=3)
        if len(time_part) < 3:
            await utils.answer(message, self.strings["invalid_time"])
            return

        time_str = " ".join(time_part[:3])
        text = " ".join(time_part[3:])
        remind_time = await self._parse_time(time_str)

        if not remind_time:
            await utils.answer(message, self.strings["invalid_time"])
            return

        self.reminder_id += 1
        self.reminders[self.reminder_id] = (text, remind_time)

        await utils.answer(
            message,
            self.strings["reminder_set"].format(text, remind_time.strftime("%d.%m.%Y %H:%M")),
        )

    @loader.command(alias="rlist")
    async def reminderlistcmd(self, message: Message):
        """Список активных напоминаний"""
        if not self.reminders:
            await utils.answer(message, self.strings["no_reminders"])
            return

        reminders_list = "\n".join(
            f"▪ <b>#{id}</b> → <i>{text}</i> (<code>{time.strftime('%d.%m.%Y %H:%M')}</code>)"
            for id, (text, time) in self.reminders.items()
        )

        await utils.answer(
            message,
            self.strings["reminder_list"].format(reminders_list),
        )

    @loader.command(alias="rdel")
    async def reminderdelcmd(self, message: Message):
        """Удалить напоминание. Пример: .rdel 1"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit() or int(args) not in self.reminders:
            await utils.answer(message, self.strings["not_found"])
            return

        del self.reminders[int(args)]
        await utils.answer(
            message,
            self.strings["reminder_deleted"].format(args),
        )