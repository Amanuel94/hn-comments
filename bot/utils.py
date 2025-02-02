import html
from datetime import datetime
from bs4 import BeautifulSoup

from .config import HN_URL


def slug(x: str, kid: int) -> str:
    return f"{x}/{kid}.json"


def get_args(msg, delimiter=" "):

    stripped = msg.strip().split(delimiter)
    if len(stripped) > 1:
        return stripped[1:]
    return None


def template(luser, karma, by, text, time):
    time = datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
    msg = ""
    msg += f"By **[{by}]({luser})**  ⭐️ {karma} \n"
    msg += "\n"
    msg += f"{text}\n\n"
    msg += f"**{time}**\n"
    return msg


def parse_xml(xml):
    return html.unescape(BeautifulSoup(xml, "html.parser").text)


def user_url(uid):
    return f"{HN_URL}user?id={uid}"


def item_url(iid):
    return f"{HN_URL}item?id={iid}"
