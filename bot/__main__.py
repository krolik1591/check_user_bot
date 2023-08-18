import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from bot import main_handler
from bot.handlers import routers


async def main(bot):
    logging.basicConfig(level=logging.WARNING)

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    for router in routers:
        dp.include_router(router)
    dp.include_router(main_handler.router)

    try:
        print("me:", await bot.me())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    TOKEN = '6060413264:AAHQifp8CbsQI6kXcQ2MdFN9cgZQQeFqw0c'

    loop = asyncio.get_event_loop()

    bot = Bot(TOKEN, parse_mode="HTML")
    asyncio.run(main(bot))
    # loop.create_task(main(bot))
