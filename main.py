import asyncio

from bot.config import logger
from webhook import run


async def main():
    logger.info("Running app...")
    await run()


if __name__ == "__main__":
    asyncio.run(main())
