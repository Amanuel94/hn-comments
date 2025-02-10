from limits import RateLimitItemPerSecond, storage, strategies
from telebot.types import Message
from .config import RATE_LIMIT, TIME_FRAME, logger


def rate_limiter(func):

    store = storage.MemoryStorage()
    fixed_window = strategies.FixedWindowRateLimiter(store)
    limiter = RateLimitItemPerSecond(RATE_LIMIT, TIME_FRAME)

    async def wrapper(message: Message, *args, **kwargs):
        # key = f"{message.from_user.id}"
        # if not fixed_window.hit(limiter, key):
        #     logger.info(f"User {message.from_user.id} is being rate limited.")
        #     await bot.send_message(
        #         message.chat.id,
        #         text="You are being rate limited. Please wait a while before trying again.",
        #     )
        #     return
        return await func(message, *args, **kwargs)

    return wrapper
