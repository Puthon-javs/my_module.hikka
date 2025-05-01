from hikkatl.types import Message
from .. import loader, utils
import json
import os

@loader.tds
class QuickNotesMod(loader.Module):
    """Сохраняй и управляй заметками прямо в Telegram"""
    strings = {
        "name": "QuickNotes",
        "saved": "📝 <b>Заметка сохранена!</b> (ID: <code>{}</code>)",
        "no_args": "❌ <b>Укажите текст заметки!</b>",
        "deleted": "🗑 <b>Заметка удалена!</b> (ID: <code>{}</code>)",
        "not_found": "🔍 <b>Заметка не найдена!</b>",
        "notes_list": "📋 <b>Ваши заметки:</b>\n\n{}",
        "note_empty": "📭 <b>У вас пока нет заметок.</b>",
        "note_content": "📄 <b>Заметка #{}</b>:\n\n<code>{}</code>",
    }

    def __init__(self):
        self.notes_file = "quicknotes.json"
        self.notes = self._load_notes()

    def _load_notes(self):
        if not os.path.exists(self.notes_file):
            return {}
        with open(self.notes_file, "r") as f:
            return json.load(f)

    def _save_notes(self):
        with open(self.notes_file, "w") as f:
            json.dump(self.notes, f)

    @loader.command(alias="sn")
    async def savenotecmd(self, message: Message):
        """Сохранить заметку. Использование: .savenote <текст>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"])
            return

        note_id = str(len(self.notes) + 1)
        self.notes[note_id] = args
        self._save_notes()

        await utils.answer(
            message,
            self.strings["saved"].format(note_id)
        )

    @loader.command(alias="dn")
    async def deletenotecmd(self, message: Message):
        """Удалить заметку. Использование: .deletenote <ID>"""
        args = utils.get_args_raw(message)
        if not args or args not in self.notes:
            await utils.answer(message, self.strings["not_found"])
            return

        del self.notes[args]
        self._save_notes()

        await utils.answer(
            message,
            self.strings["deleted"].format(args)
        )

    @loader.command(alias="ln")
    async def listnotescmd(self, message: Message):
        """Показать все заметки. Использование: .listnotes"""
        if not self.notes:
            await utils.answer(message, self.strings["note_empty"])
            return

        notes_list = "\n".join(
            f"▪ <b>#{id}</b> → {note[:30]}..." if len(note) > 30 else f"▪ <b>#{id}</b> → {note}"
            for id, note in self.notes.items()
        )

        await utils.answer(
            message,
            self.strings["notes_list"].format(notes_list)
        )

    @loader.command(alias="gn")
    async def getnotecmd(self, message: Message):
        """Показать заметку по ID. Использование: .getnote <ID>"""
        args = utils.get_args_raw(message)
        if not args or args not in self.notes:
            await utils.answer(message, self.strings["not_found"])
            return

        await utils.answer(
            message,
            self.strings["note_content"].format(args, self.notes[args])
        )