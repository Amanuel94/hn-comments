import asyncio
from dotenv import load_dotenv
import os 
from telebot.async_telebot import AsyncTeleBot

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
bot = AsyncTeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)


def start():
    asyncio.run(bot.polling())
