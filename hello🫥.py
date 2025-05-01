from hikkatl.types import Message
from .. import loader, utils
import re

@loader.tds
class AutoReactionMod(loader.Module):
    """Автоматически ставит реакции на сообщения"""
    strings = {
        "name": "AutoReaction",
        "cfg_auto_like": "Автолайкинг своих сообщений",
        "cfg_reaction_rules": "Правила реакций (формат: 'слово:эмоджи')",
        "cfg_blacklist": "Чёрный список чатов (ID через запятую)",
        "liked_msg": "👍 <b>Автолайк поставлен!</b>",
        "reaction_added": "{} <b>Реакция добавлена на:</b> <i>{}</i>",
        "stats": "📊 <b>Статистика реакций:</b>\n\n{}",
        "no_stats": "📭 <b>Статистика пуста!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_like",
                True,
                lambda: self.strings["cfg_auto_like"],
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "reaction_rules",
                "люблю:❤️,спасибо:🙏,почему:🤔",
                lambda: self.strings["cfg_reaction_rules"],
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "blacklist",
                "",
                lambda: self.strings["cfg_blacklist"],
                validator=loader.validators.String()
            ),
        )
        self.reaction_stats = {}

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message: Message):
        # Проверка чёрного списка
        chat_id = utils.get_chat_id(message)
        if str(chat_id) in self.config["blacklist"].split(","):
            return

        # Автолайкинг своих сообщений
        if self.config["auto_like"] and message.out:
            try:
                await message.react("❤️")
                self.update_stats("❤️")
            except:
                pass

        # Реакции по триггерам
        if message.text:
            text = message.text.lower()
            for rule in self.config["reaction_rules"].split(","):
                if ":" not in rule:
                    continue
                word, emoji = rule.split(":", 1)
                if word.strip() in text:
                    try:
                        await message.react(emoji.strip())
                        self.update_stats(emoji.strip())
                    except:
                        pass

    def update_stats(self, emoji: str):
        """Обновляет статистику реакций"""
        self.reaction_stats[emoji] = self.reaction_stats.get(emoji, 0) + 1

    @loader.command(alias="rstats")
    async def reactionstatscmd(self, message: Message):
        """Показать статистику реакций"""
        if not self.reaction_stats:
            await utils.answer(message, self.strings["no_stats"])
            return

        stats_text = "\n".join(
            f"▪ {emoji} — {count} раз"
            for emoji, count in sorted(
                self.reaction_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )
        await utils.answer(
            message,
            self.strings["stats"].format(stats_text)
        )

    @loader.command(alias="addreact")
    async def addreactioncmd(self, message: Message):
        """Добавить правило реакции. Пример: .addreact привет:👋"""
        args = utils.get_args_raw(message)
        if not args or ":" not in args:
            await utils.answer(message, "❌ <b>Используйте:</b> <code>.addreact слово:эмоджи</code>")
            return

        word, emoji = args.split(":", 1)
        current_rules = self.config["reaction_rules"]
        if current_rules:
            current_rules += ","
        self.config["reaction_rules"] = current_rules + f"{word.strip()}:{emoji.strip()}"
        
        await utils.answer(
            message,
            self.strings["reaction_added"].format(emoji.strip(), word.strip())
        )