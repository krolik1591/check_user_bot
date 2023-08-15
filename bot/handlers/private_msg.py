import json

from aiogram import F, Router, types
from aiogram.filters import Command, Text

from bot.db.methods import create_new_promo, get_user_promos, is_promo_in_db
from bot.utils.config_reader import config

router = Router()


@router.message(F.chat.type == "private", Command("add_promo"))
async def add_promo(message: types.Message):
    admins = config.admin_ids
    if str(message.from_user.id) not in admins:
        return

    promo_name = message.text.removeprefix('/add_promo')
    if not promo_name:
        await message.answer("Введіть промо!")
        return

    if await is_promo_in_db(promo_name):
        await message.answer(f'Промо з назвою {promo_name} вже існує!')
        return

    await create_new_promo(message.from_user.id, promo_name.lstrip())
    await message.answer(f'Промокод<code>{promo_name}</code> створено!')


@router.message(F.chat.type == "private", Command("my_promos"))
async def my_promos(message: types.Message):
    active_promos = json.loads(await get_user_promos(message.from_user.id))
    if not active_promos:
        await message.answer('У вас немає промокодів!')
        return
    text = '\n'.join(active_promos)
    await message.answer(f'Ваші промокоди:\n{text}')
