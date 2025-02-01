import requests

from .config import bot, BASE_API_URL
from .utils import get_arg, slug
from .commands import cmds


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(commands=[cmds['list']['name']])
async def get_comments(message):
    sanitized = get_arg(message.text)
    req = BASE_API_URL + slug('item', sanitized)
    print(req)
    resp = requests.get(req)
    print(resp.content)
    await bot.reply_to(message, message.text)