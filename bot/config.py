from dotenv import load_dotenv
import os 
from telebot.async_telebot import AsyncTeleBot
load_dotenv ()

API_TOKEN = os.getenv('API_TOKEN')
DEFAULT_PAGE_SIZE = 15
API_VERSION = 'v0'
BASE_API_URL = ' https://hacker-news.firebaseio.com/' + API_VERSION + '/'

bot = AsyncTeleBot(API_TOKEN)
