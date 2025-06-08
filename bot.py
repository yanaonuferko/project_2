import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from routers import commands, admin
from utils.logger import logger
from middlewares.logger import LoggingMiddleware, ThrottlingMiddleware
from middlewares.user_management import UserManagementMiddleware
from config.settings import RATE_LIMIT


async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Welcome message and brief introduction"),
        BotCommand(command="help", description="Show this help message"),
        BotCommand(command="quote", description="Get a random inspirational quote"),
        BotCommand(command="favorites", description="View favorite quotes"),
        BotCommand(command="language", description="Change interface language"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Bot commands set successfully")


async def main():
    """Основная функция запуска бота"""
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Подключение middleware
    dp.message.middleware(UserManagementMiddleware())
    dp.callback_query.middleware(UserManagementMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(ThrottlingMiddleware(rate_limit=RATE_LIMIT))
    
    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(admin.router)
    # Логирование старта бота
    logger.info("Bot is starting...")
    logger.info(f"Rate limiting enabled: {RATE_LIMIT} seconds between messages")
    
    try:
        # Установка команд бота
        await set_commands(bot)
        
        # Запуск поллинга
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")