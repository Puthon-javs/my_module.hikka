from hikkatl.types import Message
from .. import loader, utils
import requests

@loader.tds
class CurrencyConverterMod(loader.Module):
    """Конвертер валют (типо как у крутых банков)"""
    strings = {"name": "CurrencyConverter"}

    async def client_ready(self, client, db):
        self._client = client

    @loader.command()
    async def convert(self, message: Message):
        """<сумма> <из валюты> <в валюту> - Конвертировать валюту"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "🚫 <b>ну ты чё, а аргументы?</b>\nПример: <code>.convert 100 USD RUB</code>")
            return

        try:
            amount, from_curr, to_curr = args.split()
            amount = float(amount)
        except:
            await utils.answer(message, "😤 <b>это же не числа!</b>\nПиши типа: <code>.convert 100 EUR USD</code>")
            return

        # Тут API (я юзала бесплатное exchangerate-api.com)
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        response = requests.get(url).json()
        rate = response["rates"][to_curr.upper()]
        result = round(amount * rate, 2)

        await utils.answer(
            message,
            f"💱 <b>Результат:</b> {amount} {from_curr.upper()} = <u>{result}</u> {to_curr.upper()}\n"
            f"<i>(Курс: 1 {from_curr.upper()} = {rate} {to_curr.upper()})</i>"
        )
