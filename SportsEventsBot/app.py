import asyncio
from aiogram import executor
from config import admin_id
from database import create_db
from load_all import bot
from admin_panel import DELAY, repeat, mailing


async def on_shutdown(dp):
    await bot.close()


async def on_startup(dp):
    await create_db()
    await bot.send_message(admin_id, "Бот запущен!\n"
                                     "Нажмите /menu")
    from admin_panel import mailing
    await mailing()


if __name__ == '__main__':
    from admin_panel import dp
    from handlers import dp

    loop = asyncio.get_event_loop()
    loop.call_later(DELAY, repeat, mailing(), loop)
    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup, loop=loop)

