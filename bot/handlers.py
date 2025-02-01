import requests
from telegram.constants import ParseMode
from .api import get_comment, get_kids, get_user_karma
from .commands import cmds
from .config import DEFAULT_PAGE_SIZE, bot
from .utils import get_arg, template, user_url, item_url, parse_xml


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


@bot.message_handler(commands=[cmds['list']['name']])
async def get_comments(message, page_size = DEFAULT_PAGE_SIZE, page = 0):
    try:
        id = get_arg(message.text)
        kids = get_kids(id)[page:page+page_size]
        comments = [get_comment(kid) for kid in kids]
        for comment in comments:
            msg = template(
                user_url(comment['by']),
                item_url(comment['id']),
                get_user_karma(comment['by']),
                comment['by'],
                parse_xml(comment['text']),
                comment['time']
            )
            await bot.reply_to(message, msg, parse_mode="Markdown")
    except Exception as e:
       raise e

    
