from .games import router as games_router
from .private_msg import router as admin_router

routers = [
    admin_router,
    games_router,   # may be last
]
