import random
from pprint import pprint

from aiogram import F, Router, types
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from bot.consts.player_lvl import PLAYER_LVLS
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
    if not await db.is_user_exists(message.from_user.id):
        await db.add_new_user(message.from_user.id, message.from_user.username)

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
    if not await db.is_user_exists(message.from_user.id):
        await db.add_new_user(message.from_user.id, message.from_user.username)

    await db.add_game_result(message.from_user.id, emoji, dice_value)


@router.message(Command("stats"))
async def stats(message: types.Message):
    all_stats = await db.get_user_stats(message.from_user.id)

    bowling_stat = all_stats.get('🎳', '')
    bowling_point = bowling_stat.count('2') + \
                  bowling_stat.count('3') * 3 + \
                  bowling_stat.count('4') * 4 + \
                  bowling_stat.count('5') * 5 + \
                  bowling_stat.count('6') * 6
    football_point = sum(1 for char in all_stats.get('⚽', '') if char in '345')
    basket_point = sum(1 for char in all_stats.get('🏀', '') if char in '45')

    points_sum = bowling_point + football_point + basket_point

    player_lvl = ''
    for point, name in PLAYER_LVLS.items():
        if points_sum < point:
            player_lvl = name
            break

    text = f"@{message.from_user.username} {message.from_user.id} Твій результат:\n" \
           f"⚽ Забито голів: {football_point}\n" \
           f"🏀 Закинуто м'ячів: {basket_point}\n" \
           f"🎳 Збито кеглів: {bowling_point}\n" \
           f"       Страйків: {bowling_stat.count('6')}\n\n" \
           f"Твій статус гравця: {player_lvl}"

    await message.answer(f'Статистика:\n\n{text}')
