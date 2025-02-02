import asyncio

from bot import bot
from bot.utils import parse_xml
from bot.config import logger

if __name__ == "__main__":
    logger.info("Bot started")
    asyncio.run(bot.polling())
