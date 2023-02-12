from typing import List


def get_combo_text(dice_value: int) -> List[str]:
    values = ["BAR", "виноград", "лимон", "семь"]

    return [values[(dice_value - 1) // i % 4] for i in (1, 4, 16)]


def get_coefficient(dice_value: int) -> float:
    result = get_combo_text(dice_value)

    def is_two_items(x):
        return result.count(x) == 2 and result[1] == x

    def is_three_items(x):
        return result.count(x) == 3

    if is_three_items('семь'):
        return 20
    if is_three_items('виноград'):
        return 10
    if is_three_items('лимон'):
        return 5
    if is_three_items('BAR'):
        return 3

    if is_two_items('семь'):
        return 1
    if is_two_items('виноград'):
        return 0.5
    if is_two_items('лимон') or is_two_items('BAR'):
        return 0.25
    return 0


if __name__ == '__main__':
    for i in range(1, 65):
        print(i, get_combo_text(i))
