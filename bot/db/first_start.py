from .models import Promocodes, User, GameLog, manager

async def first_start():
    if User.table_exists():
        return

    print("First start, creating tables...")

    await manager.create_tables(User, GameLog, Promocodes)
