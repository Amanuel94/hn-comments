import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import aiohttp
from telebot.types import Update
from flask import Flask, request
from bot.config import bot, logger, HOST, PORT, WEBHOOK_URL, WEBHOOK_URL_PATH
from threading import Thread

from bot.handlers import send_welcome


app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
async def webhook():
    logger.debug("Getting request...")
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True))
        logger.debug("Procesing Updates...")
        # bot.close_session()
        bot.process_new_updates(updates=[update])
        # bot.close_session()
        return "OK"


@app.route("/test", methods=["GET"])
def test():
    logger.debug("Getting request...")
    return "Helllo"


async def config_webhook():
    logger.debug("In config_webhook")
    res = bot.set_webhook(WEBHOOK_URL)
    if not res:
        raise Exception("Couldn't set webhook")
    info = bot.get_webhook_info()
    logger.debug(info)


async def delete_webhook():
    logger.debug("In delete_webhook")
    res = bot.delete_webhook(drop_pending_updates=True)
    if not res:
        logger.warning("Couldn't delete webhook")


async def run():
    await delete_webhook()
    await config_webhook()
    app.run(host=HOST, port=PORT)
