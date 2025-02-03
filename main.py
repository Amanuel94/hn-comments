import asyncio

from bot import bot
from bot.config import logger
from pinger import pinger

if __name__ == "__main__":
    logger.info("Bot started")
    pinger()
    asyncio.run(bot.polling())
