from enum import Enum
from typing import List


class Slot(Enum):
    BAR = "➖"
    GRAPES = "🍇"
    LEMON = "🍋"
    SEVEN = "7️⃣"

    def __str__(self):
        return self.value


dices = [Slot.BAR, Slot.GRAPES, Slot.LEMON, Slot.SEVEN]


def get_casino_text(dice_value):
    result = parse_dice(dice_value)

    for condition, reward in SLOTS_TEXT.items():
        if condition(result):
            return reward

    return 'Не пощастило :('


def two_near(x):
    return lambda slot_result: slot_result.count(x) == 2 and slot_result[1] == x


def two(x):
    return lambda slot_result: slot_result.count(x) == 2 and slot_result[1] != x


def three(x):
    return lambda slot_result: slot_result.count(x) == 3


def parse_dice(dice_value: int) -> List[Slot]:
    dice_value -= 1
    return [
        dices[dice_value // i % 4]
        for i in (1, 4, 16)
    ]


SLOTS_TEXT = {
    three(Slot.SEVEN): '🤑 <b>Джекпот!</b> 🤑',
    three(Slot.LEMON): 'Три в ряд 🍋',
    three(Slot.GRAPES): 'Три в ряд 🍇',
    three(Slot.BAR): 'Три в ряд ➖',

    two_near(Slot.SEVEN): 'Два поруч 7️⃣',
    two_near(Slot.GRAPES): 'Два поруч 🍇',
    two_near(Slot.LEMON): 'Два поруч 🍋',
    two_near(Slot.BAR): 'Два поруч ➖',

    two(Slot.SEVEN): 'Два 7️⃣',
    two(Slot.GRAPES): 'Два 🍇',
    two(Slot.LEMON): 'Два 🍋',
    two(Slot.BAR): 'Два ➖',
}


if __name__ == '__main__':
    x = get_casino_text(45, SLOTS_TEXT)
    print(x)
