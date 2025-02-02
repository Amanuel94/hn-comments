import aiohttp, asyncio, json
from telebot.util import quick_markup
from telebot.types import Message
import time

from .api import get_comment, get_info, get_user_karma
from .commands import cmds
from .config import DB_NAME, DEFAULT_PAGE_SIZE, bot
from .middleware import rate_limiter
from .utils import get_args, template, user_url, item_url, parse_xml
from database import Database


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


async def save_story(db, iid, userid):
    return db.insert(userid, iid)


async def delete_story(db, iid, userid):
    return db.delete(iid, userid)


async def list_bookmarks(db, userid):
    return db.search(userid)


# handlers


@bot.message_handler(commands=["help", "start"])
@rate_limiter
async def send_welcome(message):
    try:
        args = get_args(message.text)
        if args:
            if args[0].startswith(cmds["list"]["name"]):
                iid, *_ = get_args(args[0], delimiter="_")
                await list_comments(iid, message)
            elif args[0].startswith(cmds["bookmark"]["name"]):
                iid, *_ = get_args(args[0], delimiter="_")
                await save_story(iid, message.chat.id)
            return
    except Exception as e:
        await bot.send_message(message.chat.id, text=f"An error occurred: {str(e)}")

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


@bot.message_handler(commands=[cmds["bookmark"]["name"]])
@rate_limiter
async def bookmark(message):
    args = get_args(message.text)
    if not args:
        await bot.send_message(message.chat.id, text="Please provide a story id")
        return

    await bot.send_message(message.chat.id, text="Bookmarking story...")
    iid = args[0]

    with Database(DB_NAME) as db:
        res = await save_story(db, iid, message.chat.id)
        if not res:
            await bot.send_message(
                message.chat.id,
                text="Failed to create bookmark. Check if story is already bookmarked by using /bookmarks",
            )
            return

    await bot.send_message(message.chat.id, text="Story bookmarked")


@bot.message_handler(commands=[cmds["bookmarks"]["name"]])
@rate_limiter
async def bookmarks(message):
    with Database(DB_NAME) as db:
        res = await list_bookmarks(db, message.chat.id)
        if not res:
            await bot.send_message(message.chat.id, text="No bookmarks found")
            return

        msg = "Bookmarks:\n\n"
        tasks = [asyncio.create_task(get_info(row[2])) for row in res]
        for i, row in enumerate(res):
            story = await tasks[i]
            story_title = json.loads(story.content)["title"]
            msg += f"[{story_title}]({item_url(row[2])}) | Story ID: {row[2]}\n"

        await bot.send_message(message.chat.id, text=msg, parse_mode="Markdown")


@bot.message_handler(commands=[cmds["delete"]["name"]])
@rate_limiter
async def delete(message):
    args = get_args(message.text)
    if not args:
        await bot.send_message(message.chat.id, text="Please provide a bookmark id")
        return

    with Database(DB_NAME) as db:
        res = await delete_story(db, args[0], message.chat.id)
        if not res:
            await bot.send_message(
                message.chat.id,
                text="Failed to delete bookmark. Check if bookmark exists by using /bookmarks",
            )
            return

    await bot.send_message(message.chat.id, text="Bookmark deleted")
