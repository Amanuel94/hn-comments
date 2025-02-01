from datetime import datetime
from .config import HN_URL

import html
from bs4 import BeautifulSoup


def slug(x, id):
    return f'{x}/{id}.json' 

def get_arg(msg):
    msg = " ".join(msg.strip().split(' ')[1:])
    return msg

def template(luser, lcomment, karma, by, text, time):
    time = datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
    msg = ""
    msg += f"User: **[{by}]({luser})**:  ⭐️ {karma} \n"
    msg += "\n"
    msg += f"{text}\n"
    msg += f"**{time}**\n"
    return msg

def parse_xml(xml):
    return html.unescape(BeautifulSoup(xml, 'html.parser').text)

def user_url(id):
    return f'{HN_URL}/user?id={id}'

def item_url(id):
    return f'{HN_URL}/item?id={id}'
    