import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from bot.db import first_start
from bot.handlers import routers
from bot.utils.config_reader import config


async def main(bot):
    logging.basicConfig(level=logging.WARNING)

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    for router in routers:
        dp.include_router(router)

    # dp.message.middleware(ThrottlingMiddleware())
    # dp.callback_query.middleware(ThrottlingMiddleware())

    await set_private_commands(bot)
    await set_chat_commands(bot)

    await first_start()

    try:
        print("me:", await bot.me())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


async def set_chat_commands(bot: Bot):
    await bot.set_my_commands(commands=[
        types.BotCommand(command="casino", description="/casino 'number"),
        types.BotCommand(command="games", description="Список ігор"),
        types.BotCommand(command="roll_cube", description="Кубик"),
        types.BotCommand(command="roll_darts", description="Дартс"),
        types.BotCommand(command="roll_basket", description="Баскет"),
        types.BotCommand(command="roll_football", description="Футбол"),
        types.BotCommand(command="roll_casino", description="Казино"),
        types.BotCommand(command="roll_bowling", description="Боулінг"),
    ], scope=types.BotCommandScopeAllGroupChats())


async def set_private_commands(bot: Bot):
    await bot.set_my_commands(commands=[
        types.BotCommand(command="my_promos", description="Мої промокоди"),
        types.BotCommand(command="add_promo", description="Додати промо"),
        types.BotCommand(command="stats", description="Cтатистика"),
        types.BotCommand(command="admin_stats", description="Адмін статистика"),
    ], scope=types.BotCommandScopeAllPrivateChats())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    bot = Bot(config.bot_token.get_secret_value(), parse_mode="HTML")
    asyncio.run(main(bot))
    # loop.create_task(main(bot))
