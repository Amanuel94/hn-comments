import asyncio
from bot import bot, send_welcome
import os
from bot.config import logger, HOST, PORT, API_TOKEN
from webhook import app, config_webhook, delete_webhook, run
from telebot.async_telebot import AsyncTeleBot


async def main():
    logger.info("Running app...")
    await run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("here")
        asyncio.run(bot.close_session)
