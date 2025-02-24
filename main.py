import asyncio
import atexit
import datetime
import aiohttp
from flask import Flask, request
import threading

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
import tldextract


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


async def make_req(url, session):
    async with session.get(url) as response:
        if response.status != 200:
            logger.error("Error: %s, make_req", response.status)
            return []
        return await response.json()


def filter_posted(all_top_stories):
    all_top_stories = list(map(str, all_top_stories))
    with MongoDatabase(MONGO_DB_NAME) as db:
        return set(all_top_stories) - set(db.search_stories(all_top_stories))


async def execute_job():

    logger.debug("Getting cron request...")
    url = BASE_API_URL + "topstories.json"

    async with aiohttp.ClientSession() as hn_session:
        all_top_stories = await make_req(url, hn_session)
        top_stories = filter_posted(all_top_stories)

        urls = list(map(lambda x: BASE_API_URL + slug("item", x), top_stories))
        tasks = [asyncio.create_task(make_req(url, hn_session)) for url in urls]
        posted = []

        # a different session has to be used for telegram otherwise telebot destroys session for message handlers
        async with aiohttp.ClientSession() as tg_session:
            while tasks:

                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                logger.debug("Remaining: %d/%d", len(tasks), len(top_stories))
                for task in done:
                    story = await task

                    if not story:
                        logger.error("Failed to get story")
                        tasks.remove(task)
                        continue

                    if (
                        story.get("score", None) is None
                        or story["score"] < TOP_STORY_SCORE
                    ):
                        logger.debug("Story score is too low or undefined")
                        tasks.remove(task)
                        continue

                    if story.get("deleted", False):
                        tasks.remove(task)
                        logger.debug("Story is deleted")
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

                    msg = (
                        f"*{story['title']}*\n"
                        f"`- score: {story['score']} {activity}`\n"
                        f"`- posted: {display_time} ago`\n\n"
                    )
                    if story.get("url", None):
                        u = tldextract.extract(story["url"])
                        domain = u.domain
                        if u.suffix:
                            domain += "." + u.suffix

                        msg += "Read: |" + f"[{domain}]({story['url']})" + "|"

                    markup = InlineKeyboardMarkup()
                    markup.row_width = 1

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

                    payload = {
                        "chat_id": CHANNEL_ID,
                        "text": msg,
                        "parse_mode": "Markdown",
                        "reply_markup": markup.to_dict(),
                    }

                    async with tg_session.post(
                        f"https://api.telegram.org/bot{bot.token}/sendMessage",
                        json=payload,
                    ) as response:
                        if response.status != 200:
                            logger.error(
                                "Failed to send message: %s", await response.text()
                            )

                            response_data = await response.json(
                                encoding=response.get_encoding()
                            )
                            if response_data.get("error_code", None) == 429:
                                logger.error("Rate limit exceeded")
                                await asyncio.sleep(
                                    response_data["parameters"]["retry_after"] + 1
                                )
                                return

                        else:
                            posted.append(str(story["id"]))
                            tasks.remove(task)

            try:
                with MongoDatabase(MONGO_DB_NAME) as db:
                    db.post_stories(posted)
            except Exception as e:
                logger.error("Failed to post story: %s", e)


@app.route("/cron", methods=["GET", "HEAD"])
async def cron():

    thread = threading.Thread(target=lambda: asyncio.run(execute_job()))
    thread.daemon = True
    thread.start()
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
    if DEVELOPMENT == "True":
        app.run(host=HOST, port=PORT, debug=True)
