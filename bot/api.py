import aiohttp
import asyncio, json, requests
from .config import BASE_API_URL
from .utils import slug


async def get_comment(id):
    req = BASE_API_URL + slug("item", id)
    task = requests.get(req)
    return task


async def get_info(id):
    req = BASE_API_URL + slug("item", id)
    task = requests.get(req)
    return task


def get_user_karma(id):
    if id == "":
        return
    req = BASE_API_URL + slug("user", id)
    task = requests.get(req)
    return json.loads(task.content)["karma"]
