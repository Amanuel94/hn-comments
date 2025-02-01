import asyncio
from bot import bot
from bot.utils import parse_xml

if __name__ == "__main__":
    print("Restarting Bot")
    asyncio.run(bot.polling())
