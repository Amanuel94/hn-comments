import asyncio
from bot import bot

if __name__ == "__main__":
    asyncio.run(bot.polling())