import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from bot.main_handler import router as main_router


async def main(bot):
    logging.basicConfig(level=logging.WARNING)

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    dp.include_router(main_router)

    await set_private_commands(bot)

    try:
        print("me:", await bot.me())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


async def set_private_commands(bot: Bot):
    await bot.set_my_commands(commands=[
        types.BotCommand(command="admin_stats", description="Адмін статистика"),
    ], scope=types.BotCommandScopeAllPrivateChats())


if __name__ == '__main__':
    TOKEN = '6662611233:AAELYOueyIWTHj-v6f-c1LvRtMHaO_xZ79k'

    loop = asyncio.get_event_loop()

    bot = Bot(TOKEN, parse_mode="HTML")
    asyncio.run(main(bot))
    # loop.create_task(main(bot))
