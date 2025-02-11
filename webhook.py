import asyncio
import atexit
from flask import Flask, request
from telebot.types import Update

from bot.config import bot, logger, HOST, PORT, WEBHOOK_URL
from bot.middleware import resetter

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
@resetter
async def webhook():
    logger.debug("Getting request...")

    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True))
        logger.debug("Procesing Updates...")
        await bot.process_new_updates(updates=[update])
        return "OK"


@app.route("/test", methods=["GET"])
def test():
    logger.debug("Getting test request...")
    return "Test"


async def config_webhook():

    res = await bot.set_webhook(WEBHOOK_URL)
    if not res:
        raise Exception("Couldn't set webhook")
    info = await bot.get_webhook_info()
    logger.debug(info)


async def delete_webhook():
    res = await bot.delete_webhook(drop_pending_updates=True)
    if not res:
        logger.warning("Couldn't delete webhook")


async def run():
    await config_webhook()
    app.run(host=HOST, port=PORT)


@atexit.register
def teardown():
    logger.debug("Closing client connection")
    logger.debug(asyncio.run(delete_webhook()))
    logger.debug(asyncio.run(bot.close_session()))
