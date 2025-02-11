from dotenv import load_dotenv
import logging
import os
from telebot.async_telebot import AsyncTeleBot

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
TG_BOT_CALLBACK_LINK = "https://t.me/hn_comments_bot?start={0}"

if DEVELOPMENT:
    WEBHOOK_URL = "https://fifty-ties-allow.loca.lt/webhook"
else:
    WEBHOOK_URL = "https://hn-comments.onrender.com/webhook"

WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)
WEBHOOK_SSL_CERT = "./webhook_cert.pem"
WEBHOOK_SSL_PRIV = "./webhook_pkey.pem"


bot = AsyncTeleBot(API_TOKEN)

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
