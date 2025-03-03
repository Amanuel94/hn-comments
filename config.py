import asyncio
from dotenv import load_dotenv
import logging
import os
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

DEVELOPMENT = os.getenv("DEVELOPMENT")
API_TOKEN = os.getenv("API_TOKEN")
DB_NAME = os.getenv("DB_NAME")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MONGO_URL = os.getenv("MONGO_URL")
WEBHOOK_ROUTE = os.getenv("WEBHOOK_ROUTE")

MONGO_DB_NAME = "mongo_hn_comments"
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

DEFAULT_PAGE_SIZE = 10
API_VERSION = "v0"
BASE_API_URL = f" https://hacker-news.firebaseio.com/{API_VERSION}/"
HN_URL = "https://news.ycombinator.com/"
RATE_LIMIT = 30
TIME_FRAME = 60  # seconds
TOP_STORY_SCORE = 150
HOST = "0.0.0.0"
PORT = 8443
GENERIC_ERROR_MESSAGE = "Something went wrong. Please try again later."

TG_BOT_CALLBACK_LINK = "t.me/hackernews_saver_bot?start={0}"
FORWARD_SIGNATURE = "Hacker News Saver"

if DEVELOPMENT == "True":
    WEBHOOK_URL = "https://whole-symbols-occur.loca.lt/"
    FORWARD_SIGNATURE = FORWARD_SIGNATURE + ":DEV"

bot = AsyncTeleBot(API_TOKEN)


# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEVELOPMENT == "True" else logging.WARNING)
filehandler = logging.FileHandler("bot.log")
consolehandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.addHandler(consolehandler)
