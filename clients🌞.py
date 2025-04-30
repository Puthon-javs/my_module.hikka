# meta developer: @Python_Javs

from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class TelegramClientsMod(loader.Module):
    """Показывает информацию о различных Telegram клиентах"""

    strings = {
        "name": "TelegramClients",
        "clients_info": (
            "📡 <b>Доступные Telegram клиенты:</b>\n\n"
            
            "1. <b>Official Telegram</b>\n"
            "   - Официальный клиент от Telegram\n"
            "   - 📱 Платформы: Android, iOS, Windows, macOS, Linux\n"
            "   - ⚙️ Функции: Все основные функции, секретные чаты\n"
            "   - 🌐 Сайт: https://telegram.org\n\n"
            
            "2. <b>Telegram Desktop</b>\n"
            "   - Официальный десктопный клиент\n"
            "   - 💻 Платформы: Windows, macOS, Linux\n"
            "   - ⚙️ Функции: Полная синхронизация с мобильным\n"
            "   - 🌐 Сайт: https://desktop.telegram.org\n\n"
            
            "3. <b>Nekogram X</b>\n"
            "   - Модифицированный клиент с доп. функциями\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Скрытие чатов, кастомные темы\n"
            "   - 🌐 Сайт: https://nekogram.x\n\n"
            
            "4. <b>ExteraGram</b>\n"
            "   - Открытый клиент с Material You дизайном\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Material You, переводчик\n"
            "   - 🌐 Сайт: https://github.com/exteraGram\n\n"
            
            "5. <b>AyuGram</b>\n"
            "   - Модификация с улучшенным интерфейсом\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Кастомные иконки, темы\n"
            "   - 🌐 Сайт: https://ayugram.org\n\n"
            
            "6. <b>TurboTel</b>\n"
            "   - Оптимизированный клиент для скорости\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Ускоренная работа\n"
            "   - 🌐 Сайт: https://turbotel.org\n\n"
            
            "7. <b>Plus Messenger</b>\n"
            "   - Модификация официального клиента\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Доп. настройки интерфейса\n"
            "   - 🌐 Сайт: https://plusmessenger.org\n\n"
            
            "8. <b>OwlGram</b>\n"
            "   - Клиент с улучшенным дизайном\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Кастомные иконки, темы\n"
            "   - 🌐 Сайт: https://github.com/OwlGram\n\n"
            
            "9. <b>Kotatogram</b>\n"
            "   - Модификация Telegram Desktop\n"
            "   - 💻 Платформы: Windows, macOS, Linux\n"
            "   - ⚙️ Функции: Улучшенный поиск\n"
            "   - 🌐 Сайт: https://kotatogram.github.io\n\n"
            
            "10. <b>Telegram X</b>\n"
            "   - Экспериментальный клиент от Telegram\n"
            "   - 📱 Платформы: Android\n"
            "   - ⚙️ Функции: Улучшенная скорость\n"
            "   - 🌐 Сайт: https://telegram.org/blog/telegram-x"
        )
    }

    async def clientcmd(self, message: Message):
        """Показать список Telegram клиентов"""
        await utils.answer(message, self.strings["clients_info"])