from bot.consts.casino_check import get_casino_text


def get_dice_text(emoji, dice_value):
    if emoji == '🎰':
        return get_casino_text(dice_value)

    GAMES_TEXTS = {
        '🎳': BOWLING_TEXTS,
        '🏀': BASKET_TEXTS,
        '⚽': FOOTBALL_TEXTS,
        '🎲': CUBE_TEXTS,
        '🎯': DARTS_TEXTS,
    }
    return GAMES_TEXTS[emoji][dice_value]


BASKET_TEXTS = {
    1: "😐 Мимо",
    2: "😲 Майже влучив",
    3: "😵 Застряг",
    4: "👌 <b>Гарне влучання!</b>",
    5: "🤑 <b>ЧИСТЕ ВЛУЧАННЯ!</b> 🤑"
}

DARTS_TEXTS = {
    1: "😐 Мимо",
    2: "🙄 Не пощастило",
    3: "😲 Гарна спроба",
    4: "👌 <b>Непогано </b>",
    5: "👌 <b>Гарне влучання!</b>",
    6: "🍎 <b>ПРЯМО В ЦІЛЬ!</b> 🍏"
}

BOWLING_TEXTS = {
    1: "😐 Мимо",
    2: "🙄 Не пощастило",
    3: "😲 Гарна спроба",
    4: "🤐 Без коментарів...",
    5: "СТРАААЙ...\n\nА ні, здалося)",
    6: "🤑 <b>СТРАААЙК! 🤑</b>"
}

FOOTBALL_TEXTS = {
    1: "😐 Мимо",
    2: "🙄 Відскочив...",
    3: "🤑 <b>ГОООООООЛ!</b> 🤑",
    4: "🤑 <b>ГОООООООЛ!</b> 🤑",
    5: "🤑 <b>ГОООООООЛ!</b> 🤑"
}

CUBE_TEXTS = {
    1: "1️⃣ <b>- непарне</b>",
    2: "2️⃣ <b>- парне</b>",
    3: "3️⃣ <b>- непарне</b>",
    4: "4️⃣ <b>- парне</b>",
    5: "5️⃣ <b>- непарне</b>",
    6: "6️⃣ <b>- парне</b>"
}


if __name__ == '__main__':
    x = get_dice_text('🎳', 6)
    print(x)
