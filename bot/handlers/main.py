import asyncio
import io
import random
import tempfile

from PIL import Image
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.make_image import make_image

router = Router()

TIME = 60

SPAM_LINKS = ('soo.gd', 'tinyurl.com', 'cutt.us', 'gee.su')


class Check(StatesGroup):
    check = State()


# @dp.message_handler(commands=['start', 'help'], chat_type=types.ChatType.PRIVATE)
@router.message(F.chat.type == "private", Command('start'))
async def start_handler(message: types.Message):
    await message.answer("Привіт. Я - бот для захисту твоїх чатів від спамерів. \n"
                         "Додай мене до чату і дай права адміністратора на кік та видалення повідомлень.")


# @dp.message_handler(content_types=["new_chat_members"], state='*')
@router.message(lambda msg: msg.new_chat_members)
async def on_user_join(message: types.Message, state: FSMContext):

    bot_id = state.bot.id
    if message.new_chat_members[0].id == bot_id:
        return await message.answer("Привіт, дай мені права адміністратора на кік та видалення повідомлень")

    question, answer = make_question()
    image_bytes = make_image(question, TIME)
    # image_io = io.BytesIO(image_bytes)
    # img = Image.open(image_io)
    # # Створюємо тимчасовий файл
    # with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
    #     img.save(temp_file, format="PNG")
    #     temp_file.seek(0)

    bot_message = await state.bot.send_photo(
        message.chat.id,
        photo=types.InputFile(image_bytes),
        caption=f"@{message.from_user.username}, відправте рішення арифметичної задачі,"
                " інакше будете додані до чорного списку чату.",
        reply_markup=types.ForceReply(selective=True)
    )

    await state.update_data(
        answer=answer,
        bot_message=bot_message,
        new_member_message=message
    )
    await state.set_state(Check.check)
    await asyncio.sleep(TIME)

    data = await state.get_data()
    if data and data['bot_message'] == bot_message:  # Если пользователь не ответил то data еще не очищен
        await kick_user(message.chat, message.from_user)  # и bot_message-ы совпадают.   в таком случае кикаем
        await state.finish()
    with suppress(exceptions.MessageToDeleteNotFound):
        await bot_message.delete()
        await message.delete()


# @dp.message_handler(state=Check.check, content_types=types.ContentType.ANY)
# @router.message()
async def answer_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    is_check_passed = message.text and str(data['answer']) in message.text

    if not is_check_passed:
        await kick_user(message.chat, message.from_user)

    await data['bot_message'].delete()

    try:
        await message.delete()
        if not is_check_passed:
            await data['new_member_message'].delete()
    except exceptions.MessageCantBeDeleted:
        if message.chat.type != types.ChatType.SUPERGROUP:
            await message.answer('У мене немає прав на видалення повідомлень, '
                                 'тому я буду спамити цим попередженням :)')
    await state.finish()  # Пользователь ответил, стейт = None


# @dp.message_handler(state='*')
# @router.message()
async def spam_filter(message: types.Message, state: FSMContext):
    if any(message.text.startswith(i) for i in SPAM_LINKS):
        with suppress(exceptions.TelegramAPIError):
            await kick_user(message.chat, message.from_user)
            await message.delete()


def make_question():
    a, b, c = [random.randint(1, 9) for _ in range(3)]
    question = f'{a} + {b} * {c}'
    answer = a + b * c
    return question, answer


async def kick_user(chat: types.Chat, user: types.User):
    try:
        await chat.kick(user.id, until_date=int(time()) + 35)  # бан на 35 сек. <30 = inf
    except exceptions.ChatAdminRequired:
        await bot.send_message(chat.id, f'Я б із задоволенням кікнув {user.mention}, але в мене немає адмінки :(')
