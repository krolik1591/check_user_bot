from aiogram import Router, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from bot.const import START_POINTS, MIN_BET, MAX_BET
from bot.keyboards import inline_keyboard

flags = {"throttling_key": "default"}
router = Router()


@router.callback_query(text=["bet_minus", "bet_plus", "bet_min", "bet_max", "bet_x2"])
async def bet_change(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_bet = user_data.get('bet', MIN_BET)
    user_balance = user_data.get('balance', START_POINTS)

    if call.data == 'bet_minus':
        new_user_bet = user_bet - MIN_BET
    elif call.data == 'bet_plus':
        new_user_bet = user_bet + MIN_BET
    elif call.data == 'bet_min':
        new_user_bet = MIN_BET
    elif call.data == 'bet_max':
        new_user_bet = MAX_BET
    elif call.data == 'bet_x2':
        new_user_bet = user_bet * 2
    else:
        raise Exception()

    if new_user_bet > MAX_BET: new_user_bet = MAX_BET
    if new_user_bet < MIN_BET: new_user_bet = MIN_BET
    if new_user_bet > user_balance: new_user_bet = user_balance

    if user_bet == new_user_bet:
        await call.answer()
        return

    await state.update_data(bet=new_user_bet)
    await call.message.edit_text(f'Ваші гроши: {user_balance}\n\n'
                                 'Обери розмір ставки:',
                                 reply_markup=inline_keyboard(new_user_bet, new_user_bet > user_balance))


@router.message(commands="start", flags=flags)
async def cmd_start(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_balance = user_data.get("balance", START_POINTS)
    user_bet = user_data.get("bet", MIN_BET)

    msg = await message.answer(f'Ваші гроши: {user_balance}\n\n'
                               'Обери розмір ставки:', reply_markup=inline_keyboard(user_bet, user_balance < MIN_BET))
    await state.update_data(balance=user_balance, bet=user_bet, last_msg_id=msg.message_id)


@router.callback_query(text=["end_money"])
async def demo_money(call: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    user_balance = user_data.get('balance')
    if user_balance != 0:
        await call.answer('Не обманюй')
        return
    await state.update_data(balance=START_POINTS)
    await call.answer('Людяність відновлена')

    await cmd_start(call.message, state)
    await call.message.delete()


@router.message()
async def bet_change_text(message: Message, state: FSMContext):
    await message.delete()
    try:
        new_user_bet = int(message.text)
    except ValueError:
        return

    user_data = await state.get_data()

    last_msg = user_data.get('last_msg_id')
    if last_msg is None:
        return
    user_bet = user_data.get('bet', MIN_BET)
    user_balance = user_data.get('balance', START_POINTS)

    if new_user_bet > MAX_BET: new_user_bet = MAX_BET
    if new_user_bet < MIN_BET: new_user_bet = MIN_BET
    if new_user_bet > user_balance: new_user_bet = user_balance
    if user_bet == new_user_bet:
        return

    await state.update_data(bet=new_user_bet)

    await state.bot.edit_message_text(f'Ваші гроши: {user_balance}\n\n'
                                      'Обери розмір ставки:', message.chat.id, last_msg,
                                      reply_markup=inline_keyboard(new_user_bet, new_user_bet > user_balance))
