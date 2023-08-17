import asyncio
import json
import random
from pprint import pprint

from aiogram import F, Router, types
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.consts.dice_texts import get_dice_text
from bot.consts.const import DELAY_BEFORE_SEND_RESULT, GAMES_LIST, PLAYER_LVLS
from bot.db import methods as db
from bot.utils.config_reader import config

router = Router()


@router.my_chat_member(lambda member: member.new_chat_member.status == 'member')
async def on_user_join(chat_member: types.ChatMemberUpdated, state: FSMContext):
    bot_id = state.bot.id
    if chat_member.new_chat_member.user.id == bot_id:
        inviter_user_id = chat_member.from_user.id
        admins = config.admin_ids
        if str(inviter_user_id) not in admins:
            await state.bot.send_message(chat_member.chat.id, "Тільки адмін може додавати бота!")
            await state.bot.leave_chat(chat_member.chat.id)
            return


@router.message(Command("casino"))
async def casino(message: types.Message):
    await add_user_to_db(message.from_user.id, message.from_user.username)

    user_num = message.text.removeprefix("/casino")
    try:
        user_num = int(user_num)
    except ValueError:
        await message.answer("Ви маєте ввести /casino 'number' (де number - ціле число)")
        return

    random_num = random.randint(0, 100)
    if user_num != random_num:
        await message.answer(f"Ви програли, число було {random_num}")
        return

    available_promo = await db.get_available_user_promo(message.from_user.id)
    if not available_promo:
        await message.answer("Ви вгадали!")
        return

    await db.add_new_promo_to_user(message.from_user.id, available_promo[0])
    await message.answer(f"Ви виграли промокод! Для перегляду введіть в приватних повідомленнях /my_promos")


# available emoji for dice: 🎲, 🎯, 🏀, ⚽️, 🎰, 🎳
@router.message((F.chat.type.in_(['group', 'supergroup'])) and (lambda message: message.dice is not None))
async def play(message: types.Message):
    print('play')
    try:
        dice_value = message.dice.value
        emoji = message.dice.emoji
    except AttributeError:
        return
    await message.answer('Тут буде текст')

    await add_user_to_db(message.from_user.id, message.from_user.username)

    await db.add_game_result(message.from_user.id, emoji, dice_value)


@router.message(Command("stats"))
async def stats(message: types.Message):
    await db.update_username(message.from_user.id, message.from_user.username)
    bowling_point, football_point, basket_point, points_sum, bowling_strike = await get_user_stats(message.from_user.id)

    player_lvl = ''
    for point, name in PLAYER_LVLS.items():
        if points_sum < point:
            player_lvl = name
            break

    username = message.from_user.username if message.from_user.username is not None else \
        await db.get_username_by_id(message.from_user.id)

    text = f"@{username} {message.from_user.id} Твій результат:\n" \
           f"⚽ Забито голів: {football_point}\n" \
           f"🏀 Закинуто м'ячів: {basket_point}\n" \
           f"🎳 Збито кеглів: {bowling_point}\n" \
           f"       Страйків: {bowling_strike}\n\n" \
           f"Твій статус гравця: {player_lvl}"

    await message.answer(f'Статистика:\n\n{text}')


@router.message(Command("admin_stats"))
async def admin_stats(message: types.Message):
    admins = config.admin_ids
    if str(message.from_user.id) not in admins:
        await message.answer("Тільки адмін може переглядати статистику!")
        return

    result = {}

    user_ids = await db.get_unique_users()
    for user_id in user_ids:
        _, _, _, points_sum, _ = await get_user_stats(user_id)
        result[user_id] = points_sum

    sorted_result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    text = ''
    for index, (user_id, points_sum) in enumerate(sorted_result.items(), start=1):
        username = await db.get_username_by_id(user_id)
        text += f"{index}. @{username} (id: {user_id}): {points_sum} поінтів\n"

    await message.answer(f'Адмін статистика:\n\n{text}')


@router.message(Text(startswith="/roll_"))
async def roll_command(message: types.Message, state: FSMContext):
    await add_user_to_db(message.from_user.id, message.from_user.username)

    bot_username = '@' + (await state.bot.me()).username
    game = message.text.removeprefix("/roll_").removesuffix(bot_username)

    game_emoji = GAMES_LIST[game]
    msg = await message.answer_dice(emoji=game_emoji)
    await asyncio.sleep(DELAY_BEFORE_SEND_RESULT)

    await db.add_game_result(message.from_user.id, game_emoji, msg.dice.value)

    text = get_dice_text(game_emoji, msg.dice.value)
    await message.answer(text)


@router.callback_query(Text(startswith="roll_"))
async def roll_btn(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    await add_user_to_db(call.from_user.id, call.from_user.username)

    game = call.data.removeprefix("roll_")

    game_emoji = GAMES_LIST[game]
    msg = await call.message.answer_dice(emoji=game_emoji)
    await asyncio.sleep(DELAY_BEFORE_SEND_RESULT)

    await db.add_game_result(call.from_user.id, game_emoji, msg.dice.value)

    text = get_dice_text(game_emoji, msg.dice.value)
    await call.message.answer(text)


@router.message(Command("games"))
async def games(message: types.Message):
    text = 'Список доступних ігор:'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🎲', callback_data="roll_cube"),
         InlineKeyboardButton(text='🎯', callback_data="roll_darts"),
         InlineKeyboardButton(text='🏀', callback_data="roll_basket")],
        [InlineKeyboardButton(text='⚽', callback_data="roll_football"),
         InlineKeyboardButton(text='🎳', callback_data="roll_bowling"),
         InlineKeyboardButton(text='🎰', callback_data="roll_casino")],
    ])

    await message.answer(text, reply_markup=kb)


async def get_user_stats(user_id):
    all_stats = await db.get_user_stats(user_id)

    bowling_stat = all_stats.get('🎳', '')
    bowling_strike = bowling_stat.count('6')
    bowling_point = bowling_stat.count('2') + \
                    bowling_stat.count('3') * 3 + \
                    bowling_stat.count('4') * 4 + \
                    bowling_stat.count('5') * 5 + \
                    bowling_stat.count('6') * 6
    football_point = sum(1 for char in all_stats.get('⚽', '') if char in '345')
    basket_point = sum(1 for char in all_stats.get('🏀', '') if char in '45')
    points_sum = bowling_point + football_point + basket_point

    return bowling_point, football_point, basket_point, points_sum, bowling_strike


async def add_user_to_db(user_id, username):
    if not await db.is_user_exists(user_id):
        await db.add_new_user(user_id, username)
