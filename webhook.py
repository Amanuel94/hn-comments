import asyncio
import atexit
import datetime
import aiohttp
from flask import Flask, request
import requests
from telebot.types import Update
from telebot.util import quick_markup
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.commands import cmds

from bot.api import get_info
from bot.config import (
    BASE_API_URL,
    CHANNEL_ID,
    DEVELOPMENT,
    MONGO_DB_NAME,
    TG_BOT_CALLBACK_LINK,
    TOP_STORY_SCORE,
    bot,
    logger,
    HOST,
    PORT,
    WEBHOOK_URL,
    cache,
)
from bot.middleware import resetter
from bot.utils import slug
from database import Database, MongoDatabase


async def config_webhook():

    res = await bot.set_webhook(WEBHOOK_URL)
    if not res:
        raise Exception("Couldn't set webhook")
    info = await bot.get_webhook_info()
    logger.debug(info)


def setup():
    logger.debug("Setting up webhook...")
    asyncio.run(config_webhook())


app = Flask(__name__)
setup()


@app.route("/webhook", methods=["POST"])
@resetter
async def webhook():
    logger.debug("Getting request...")

    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True))
        logger.debug("Procesing Updates...")
        await bot.process_new_updates(updates=[update])
        return "OK"


@app.route("/test", methods=["GET"])
def test():
    logger.debug("Getting test request...")
    return "Test"


async def make_req(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                logger.error("Error: %s, make_req", response.status)
                return []
            return await response.json()


def filter_posted(all_top_stories):
    all_top_stories = list(map(str, all_top_stories))
    with MongoDatabase(MONGO_DB_NAME) as db:
        return set(all_top_stories) - set(db.search_stories(all_top_stories))


@app.route("/cron", methods=["GET", "HEAD"])
async def cron():
    logger.debug("Getting cron request...")
    url = BASE_API_URL + "topstories.json"
    all_top_stories = set(await make_req(url))
    top_stories = filter_posted(all_top_stories)
    # if DEVELOPMENT == "True":
    #     top_stories = list(top_stories)[:5]

    urls = list(map(lambda x: BASE_API_URL + slug("item", x), top_stories))
    tasks = [make_req(url) for url in urls]

    for task in tasks:

        story = await task
        if not story:
            continue

        if story.get("score", None) is None or story["score"] < TOP_STORY_SCORE:
            logger.info("Story score is too low or undefined")
            continue

        logger.debug("Story: %s", story)
        if story.get("deleted", False):
            logger.info("Story is deleted")
            continue

        now = datetime.datetime.now()
        published = datetime.datetime.fromtimestamp(story["time"])
        time_diff = now - published
        hrs = time_diff.total_seconds() // 3600
        display_time = (
            str(hrs) + " hours"
            if time_diff.days == 0
            else str(time_diff.days) + " days"
        )

        activity = ""
        if hrs <= 3:
            activity = "🔥"
        if hrs <= 2:
            activity = "🔥🔥"
        if hrs <= 1:
            activity = "🔥🔥🔥"
            if story["score"] >= 200:
                activity = "🔥🔥🔥🔥"

        if time_diff.days >= 7:
            activity = "❄️"

        msg = f"**{story['title']}**\n"
        msg += f"Posted {display_time} ago \n"
        msg += f"Scored {story['score']} upvotes {activity}\n"
        if story.get("url", None):
            msg += f"[Link]({story['url']})"

        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        # logger.debug(
        #     TG_BOT_CALLBACK_LINK.format(f"{cmds['bookmark']["name"]}_" + str(story["id"]))
        # )
        markup.add(
            InlineKeyboardButton(
                text="Read Later",
                url=TG_BOT_CALLBACK_LINK.format(
                    f"{cmds['bookmark']['name']}_" + str(story["id"])
                ),
            ),
            InlineKeyboardButton(
                text="Browse Comments",
                url=TG_BOT_CALLBACK_LINK.format(
                    f"{cmds['list']['name']}_" + str(story["id"])
                ),
            ),
            InlineKeyboardButton(
                text="Read on site",
                url=f"https://news.ycombinator.com/item?id={story['id']}",
            ),
            row_width=2,
        )

        await bot.send_message(
            chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown", reply_markup=markup
        )
        with MongoDatabase(MONGO_DB_NAME) as db:
            db.post_story(str(story["id"]))

    return "OK"


async def delete_webhook():
    res = await bot.delete_webhook(drop_pending_updates=True)
    if not res:
        logger.warning("Couldn't delete webhook")


def create_app():
    setup()
    return app


@atexit.register
def teardown():
    logger.debug("Closing client connection")
    # logger.debug(asyncio.run(delete_webhook()))
    logger.debug(asyncio.run(bot.close_session()))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
