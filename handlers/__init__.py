from aiogram import Router
from handlers.bot.start import router as start_router
from handlers.bot.admin import router as admin_router
from handlers.bot.servers import router as servers_router
from handlers.bot.settings import router as settings_router
from handlers.bot.domains import router as domains_router

routers: list[Router] = [start_router, admin_router, servers_router, settings_router, domains_router]

__all__ = ['routers']

