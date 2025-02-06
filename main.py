import asyncio
from bot import bot
import os
from bot.config import logger, HOST, PORT
from webhook import app, config_webhook, delete_webhook, run
from threading import Thread


async def main():
    logger.info("Running app...")
    # app.run(host=HOST, port=PORT)
    thread = Thread(target=run)
    thread.start()
    await delete_webhook()
    await config_webhook()
    # print(await bot.run_webhooks(port=PORT))
    thread.join()


if __name__ == "__main__":
    asyncio.run(main())
