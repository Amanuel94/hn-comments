import asyncio
import atexit
import aiohttp
from flask import Flask, request
import requests
from telebot.types import Update

from bot.api import get_info
from bot.config import (
    BASE_API_URL,
    CHANNEL_ID,
    DEVELOPMENT,
    MONGO_DB_NAME,
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
        return set(all_top_stories) - db.search_stories(all_top_stories)


@app.route("/cron", methods=["GET", "HEAD"])
async def cron():
    logger.debug("Getting cron request...")
    url = BASE_API_URL + "topstories.json"
    all_top_stories = set(await make_req(url))
    top_stories = filter_posted(all_top_stories)
    if DEVELOPMENT == "True":
        top_stories = list(top_stories)[:5]

    for story_id in top_stories:
        url = BASE_API_URL + slug("item", story_id)
        story = await make_req(url)
        if not story:
            continue

        logger.debug("Story: %s", story)
        if story.get("score", None) is None or story["score"] < TOP_STORY_SCORE:
            logger.info("Story score is too low or undefined")
            continue

        with MongoDatabase(MONGO_DB_NAME) as db:
            db.post_story(str(story["id"]))
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"Story: *{story['title']}* has reached {story['score']} upvotes!",
            )

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
