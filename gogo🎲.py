from random import randint
import re
from .. import loader, utils

@loader.tds
class DiceMod(loader.Module):
    """Простой модуль для броска кубиков"""
    
    strings = {
        "name": "Dice",
        "dice": "🎲 {notation}: <b>{result}</b>",
        "error": "❌ Используй: .d [кол-во]d[грани][+мод] [h|xN]\nПримеры:\n.d 2d6\n.d d20+3 h\n.d 3d10 x5"
    }

    async def dcmd(self, message):
        """Бросок кубиков - .d [1]d20[+5] [h|x5]"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["error"])

        # Парсим аргументы
        parts = args.split()
        dice_part = parts[0].lower().replace("д", "d")
        mode = parts[1] if len(parts) > 1 else ""

        # Автодополнение (d20 → 1d20, 6 → 1d6)
        if dice_part.startswith("d"):
            dice_part = "1" + dice_part
        elif dice_part.isdigit():
            dice_part = f"1d{dice_part}"

        # Разбираем кубик (поддержка 2d10+3)
        try:
            if "+" in dice_part:
                count, rest = dice_part.split("d")
                sides, mod = rest.split("+")
                mod = int(mod)
            elif "-" in dice_part:
                count, rest = dice_part.split("d")
                sides, mod = rest.split("-")
                mod = -int(mod)
            else:
                count, sides = dice_part.split("d")
                mod = 0
            
            count = int(count) if count else 1
            sides = int(sides)
        except:
            return await utils.answer(message, self.strings["error"])

        # Проверка значений
        if count < 1 or sides < 1:
            return await utils.answer(message, "❌ Числа должны быть больше 0!")
        if count > 100 or sides > 1000:
            return await utils.answer(message, "❌ Слишком большие числа!")

        # Бросок кубиков
        result = sum(randint(1, sides) for _ in range(count)) + mod

        # Формируем ответ
        notation = f"{count}d{sides}"
        if mod > 0:
            notation += f"+{mod}"
        elif mod < 0:
            notation += f"{mod}"

        # Режимы вывода
        if "h" in mode:
            await utils.answer(message, f"🎲 {notation}: <spoiler><b>{result}</b></spoiler>")
        elif mode.startswith("x"):
            try:
                times = int(mode[1:])
                if times > 10:
                    return await utils.answer(message, "❌ Максимум 10 бросков!")
                rolls = [str(sum(randint(1, sides) for _ in range(count)) + mod) for _ in range(times)]
                await utils.answer(message, f"🎲 {notation} (×{times}):\n" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(rolls)))
            except:
                pass
        else:
            await utils.answer(message, self.strings["dice"].format(notation=notation, result=result))