from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_keyboard(bet, not_enough_money):
    keyboard = [
        [InlineKeyboardButton(text='-', callback_data="bet_minus"),
         InlineKeyboardButton(text=f'{bet}', callback_data="withdraw"),
         InlineKeyboardButton(text='+', callback_data="bet_plus")
         ],
        [
            InlineKeyboardButton(text='Мін.', callback_data="bet_min"),
            InlineKeyboardButton(text='Подвоїти', callback_data="bet_x2"),
            InlineKeyboardButton(text='Макс.', callback_data="bet_max")
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data="bet_back"),
            InlineKeyboardButton(text='Грати', callback_data="bet_play")
        ]]
    if not_enough_money:
        keyboard.insert(0, [InlineKeyboardButton(text='Віддай гроші', callback_data="end_money")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
