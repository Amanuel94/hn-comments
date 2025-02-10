import asyncio
from bot import app_, send_welcome
from bot.config import logger
from webhook import run
from telegram.ext import CommandHandler, MessageHandler, filters


async def main():
    logger.info("Running app...")
    await app_.initialize()
    msg_handler = MessageHandler(filters.TEXT, callback=send_welcome)
    app_.add_handler(msg_handler)
    await run()


if __name__ == "__main__":

    asyncio.run(main())
