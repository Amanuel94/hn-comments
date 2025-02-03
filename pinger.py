from flask import Flask
from threading import Thread
from bot.config import logger

app = Flask("")


@app.route("/")
def home():
    logger.debug("Pinged")
    return "Hello. I am alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def pinger():
    t = Thread(target=run)
    t.start()
