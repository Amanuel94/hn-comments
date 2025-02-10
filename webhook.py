import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import aiohttp
from telebot.types import Update
from flask import Flask, request
from bot.config import bot, logger, HOST, PORT, WEBHOOK_URL
from threading import Thread

from bot.handlers import send_welcome


app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
async def webhook():
    logger.debug("Getting request...")
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True))
        logger.debug("Procesing Updates...")
        # await bot.close_session()
        await bot.process_new_updates(updates=[update])
        # await bot.close_session()
        return "OK"


@app.route("/test", methods=["GET"])
def test():
    logger.debug("Getting request...")
    return "Helllo"


async def config_webhook():
    logger.debug("In config_webhook")
    res = await bot.set_webhook(WEBHOOK_URL)
    if not res:
        raise Exception("Couldn't set webhook")
    info = await bot.get_webhook_info()
    logger.debug(info)


async def delete_webhook():
    logger.debug("In delete_webhook")
    res = await bot.delete_webhook(drop_pending_updates=True)
    if not res:
        logger.warning("Couldn't delete webhook")


async def run():
    await delete_webhook()
    await config_webhook()
    app.run(host=HOST, port=PORT)
