from .games import router as games_router
from .private_msg import router as admin_router
from .main import router as main_router

routers = [
    main_router,
    admin_router,
    games_router,   # may be last
]
