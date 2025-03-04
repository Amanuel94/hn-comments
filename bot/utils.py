import html
from datetime import datetime
from bs4 import BeautifulSoup

from .config import HN_URL, logger


def slug(x: str, kid: int) -> str:
    return f"{x}/{kid}.json"


def get_args(msg, delimiter=" "):

    stripped = msg.strip().split(delimiter)
    if len(stripped) > 1:
        return stripped[1:]
    return None


def template(luser, karma, by, text, time):
    try:
        time = int(time)
        time = datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")
        msg = ""
        msg += f"By **[{by}]({luser})**  ⭐️ {karma} \n"
        msg += "\n"
        msg += f"{text}\n\n"
        msg += f"**{time}**\n"
        return msg
    except Exception as e:
        return logger.error(f"An error occurred: {str(e)} - template")


def parse_xml(xml):
    try:
        return html.unescape(BeautifulSoup(xml, "html.parser").text)
    except Exception as e:
        logger.warning(
            f"An error occurred while parsing a comment: {str(e)} - parse_xml"
        )
        return xml


def user_url(uid):
    return f"{HN_URL}user?id={uid}"


def item_url(iid):
    return f"{HN_URL}item?id={iid}"
