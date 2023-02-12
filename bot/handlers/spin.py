from asyncio import sleep

from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext

from bot.const import THROTTLE_TIME_SPIN, MIN_BET, START_POINTS
from bot.dice_check import get_coefficient
from .default_commands import cmd_start

flags = {"throttling_key": "spin"}
router = Router()


@router.callback_query(text=["bet_play"])
async def casino_play(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_balance = user_data.get("balance", START_POINTS)
    user_bet = user_data.get('bet', MIN_BET)

    if user_bet > user_balance:
        await call.message.answer("Ставка більше балансу ")
        return

    # Отправка дайса пользователю
    msg = await call.message.answer_dice(emoji="🎰")
    await call.message.edit_text(text="Успіхів!")

    # Получение информации о дайсе
    score_change = get_coefficient(msg.dice.value) * user_bet
    win_or_lose_text = "К сожалению, вы не выиграли." if score_change == 0 \
        else f"Вы выиграли {score_change} очков!"

    # Обновление счёта
    user_balance = user_balance - user_bet + score_change

    await state.update_data(balance=user_balance)

    await sleep(THROTTLE_TIME_SPIN)
    await call.message.edit_text(text=win_or_lose_text)

    await cmd_start(call.message, state)
