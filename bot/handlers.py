import aiohttp, asyncio, json
from telebot.util import quick_markup
from telebot.types import Message
import time

from .api import get_comment, get_info, get_user_karma
from .commands import cmds
from .config import DEFAULT_PAGE_SIZE, bot
from .utils import get_args, template, user_url, item_url, parse_xml


async def list_comments(iid, message: Message, page=0, page_size=DEFAULT_PAGE_SIZE):

    message = await bot.send_message(message.chat.id, text="Fetching comments...")

    res = await asyncio.create_task(get_info(iid))
    item = json.loads(res.content)
    kids, title = item["kids"][page : page + page_size], item["title"]

    if not kids:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text="No comments found" if page == 0 else "No more comments",
        )
        return

    print("Fetching comments...")
    tasks = [asyncio.create_task(get_comment(kid)) for kid in kids]
    for i, task in enumerate(tasks):

        comment = await task
        if i == 0:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=f"*Story: {title}*\n*Comments {page+1} - {page+page_size}*",
            )

        comment = json.loads(comment.content)

        msg = template(
            user_url(comment["by"]),
            get_user_karma(comment["by"]),
            comment["by"],
            parse_xml(comment["text"]),
            comment["time"],
        )

        markup = quick_markup(
            {"Read on site": {"url": item_url(comment["id"])}}, row_width=1
        )
        await bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=markup)

    next_btn = quick_markup(
        {"Next": {"callback_data": f"list_{iid}_{page+page_size}"}},
        row_width=1,
    )
    await bot.send_message(
        message.chat.id, text=f"Next {page_size} messages", reply_markup=next_btn
    )


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):

    args = get_args(message.text)
    if args:
        if args[0].startswith(cmds["list"]["name"]):
            iid, *opts = get_args(args[0], delimiter="_")
            await list_comments(iid, message)
        return

    text = "Welcome! This bot fetches comments from Hacker News.\n\n"
    await bot.send_message(message.chat.id, text)


@bot.message_handler(commands=[cmds["list"]["name"]])
async def get_comments(message):
    args = get_args(message.text)
    iid, *(opts) = args

    page = int(opts[0]) if opts else 0
    await list_comments(iid, message, page=page)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(cmds["list"]["name"])
)
async def list_callback(call):
    _, iid, *args = call.data.split("_")
    page = int(args[0]) if args else 0
    await list_comments(iid, call.message, page=page)
