import json, requests
from .config import BASE_API_URL
from .utils import slug

def get_comment(id):
    req = BASE_API_URL + slug('item', id)
    resp = requests.get(req)
    return json.loads(resp.content)

def get_kids(id):
    req = BASE_API_URL + slug('item', id)
    resp = requests.get(req)
    return json.loads(resp.content)['kids']

def get_user_karma(id):
    req = BASE_API_URL + slug('user', id)
    resp = requests.get(req)
    return json.loads(resp.content)['karma']

