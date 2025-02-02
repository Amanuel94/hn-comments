from dotenv import load_dotenv
import os
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
DB_NAME = os.getenv("DB_NAME")
DEFAULT_PAGE_SIZE = 5
API_VERSION = "v0"
BASE_API_URL = f" https://hacker-news.firebaseio.com/{API_VERSION}/"
HN_URL = "https://news.ycombinator.com/"
RATE_LIMIT = 1
TIME_FRAME = 60

bot = AsyncTeleBot(API_TOKEN)
