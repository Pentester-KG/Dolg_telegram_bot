import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from handlers import router
from aiogram.types import BotCommand  # Импортируем роутер из handlers.py

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(TOKEN)
# Подключаем роутер
dp.include_router(router)

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="add", description="Добавить должника"),
        BotCommand(command="list", description="Показать список должников"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)
# Запуск бота
async def main():
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())