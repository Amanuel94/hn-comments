from dotenv import load_dotenv
import logging
import os
from telebot.async_telebot import AsyncTeleBot
from aiogram import Bot

load_dotenv()

DEVELOPMENT = True

API_TOKEN = os.getenv("API_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DEFAULT_PAGE_SIZE = 10
API_VERSION = "v0"
BASE_API_URL = f" https://hacker-news.firebaseio.com/{API_VERSION}/"
HN_URL = "https://news.ycombinator.com/"
RATE_LIMIT = 30
TIME_FRAME = 60  # seconds
HOST = "0.0.0.0"
PORT = 8443
TG_BASE_URL = f"https://api.telegram.org/bot{API_TOKEN}/"

if DEVELOPMENT:
    WEBHOOK_URL = "https://tame-bushes-relax.loca.lt/webhook"
else:
    WEBHOOK_URL = "https://hn-comments.onrender.com/webhook"

WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

bot = AsyncTeleBot(API_TOKEN)
sender = Bot(API_TOKEN)

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEVELOPMENT else logging.INFO)
filehandler = logging.FileHandler("bot.log")
consolehandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
filehandler.setFormatter(formatter)
consolehandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.addHandler(consolehandler)
