import asyncio
from bot import bot, send_welcome
import os
from bot.config import logger, HOST, PORT
from webhook import app, config_webhook, delete_webhook, run
from threading import Thread


async def main():
    logger.info("Running app...")

    thread = Thread(target=run)
    thread.start()
    # await delete_webhook()
    await config_webhook()
    # bot.add_message_handler()

    thread.join()


if __name__ == "__main__":
    asyncio.run(main())
