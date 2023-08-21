import asyncio
import datetime
import os
import random
from time import time

from aiogram import F, Router, exceptions, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.make_image import make_image

router = Router()

TIME = 60
ADMINS = [6193913287, 357108179]


class Check(StatesGroup):
    check = State()


@router.message(F.chat.type == "private", Command('start'))
async def start_handler(message: types.Message):
    await message.answer("Привіт. Я - бот для захисту твоїх чатів від спамерів. \n"
                         "Додай мене до чату і дай права адміністратора на кік та видалення повідомлень.")


@router.my_chat_member(lambda member: member.new_chat_member.status == 'member')
async def on_bot_join(chat_member: types.ChatMemberUpdated, state: FSMContext):
    print('add_bot_to_chat')
    bot_id = state.bot.id
    if chat_member.new_chat_member.user.id == bot_id:
        inviter_user_id = chat_member.from_user.id
        if inviter_user_id not in ADMINS:
            await state.bot.leave_chat(chat_member.chat.id)
            return

        return await state.bot.send_message(chat_member.chat.id, "Привіт, дай мені права адміністратора на кік та видалення повідомлень")


@router.chat_member(lambda member: member.new_chat_member.status == 'member')
async def chat_member_handler(chat_member: types.ChatMemberUpdated, state: FSMContext):
    print('new_member_in_chat')
    new_user_id = chat_member.new_chat_member.user.id

    question, answer = make_question()
    image_bytes = make_image(question, TIME)

    bot_message = await state.bot.send_photo(
        chat_member.chat.id,
        photo=types.BufferedInputFile(image_bytes, filename="image.png"),
        caption=f"@{chat_member.new_chat_member.user.username}, відправте рішення арифметичної задачі,"
                " інакше будете додані до чорного списку чату.",
        reply_markup=types.ForceReply(selective=True)
    )

    await state.update_data(
        answer=answer,
        bot_message=bot_message,
    )
    await state.set_state(Check.check)
    await asyncio.sleep(10)

    data = await state.get_data()
    if data['bot_message'] == bot_message:  # Если пользователь не ответил то data еще не очищен
        await kick_user(state, chat_member.chat.id, new_user_id)  # и bot_message-ы совпадают.   в таком случае кикаем
        await state.set_state(None)  # и очищаем data и state

    status = 'passed' if data['bot_message'] != bot_message else 'failed'

    time_ = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open('stats.csv', 'a') as file:
        file.write(f'{chat_member.new_chat_member.user.id},{chat_member.new_chat_member.user.username},{time_},{status}\n')


@router.message(StateFilter(Check.check))
async def answer_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    is_check_passed = message.text and str(data['answer']) in message.text

    if not is_check_passed:
        await kick_user(state, message.chat.id, message.from_user.id)
    else:
        await state.update_data(bot_message=None)

    bot_message = data['bot_message']
    await state.bot.delete_message(bot_message.chat.id, bot_message.message_id)
    await message.delete()
    await state.set_state(None)


@router.message(F.chat.type == "private", Command('admin_stats'))
async def admin_stats_handler(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print('current_directory:', current_directory)
    file = types.FSInputFile(path='stats.csv', filename='stats.csv')

    await state.bot.send_document(message.from_user.id, file)


def make_question():
    a, b, c = [random.randint(1, 9) for _ in range(3)]
    question = f'{a} + {b} * {c}'
    answer = a + b * c
    return question, answer


async def kick_user(state, chat_id, user_id):
    try:
        await state.bot.ban_chat_member(chat_id, user_id, until_date=int(time()) + 35) # бан на 35 сек. <30 = inf
        await state.bot.unban_chat_member(chat_id, user_id)
    except exceptions.TelegramBadRequest:
        await state.bot.send_message(chat_id, f'Не можу кікнути юзера або видалити повідомлення, дайте адмінку')
