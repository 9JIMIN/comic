import requests
from bs4 import BeautifulSoup
import json

params = {
    "ticket": "comic",
    "pool": "cbox3",
    "lang": "kr",
    "objectId": "570503_304",
    "pageSize": "15"
}

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "referer": "https://comic.naver.com/comment/comment.nhn?titleId=570503&no=304"
}

html = requests.get(
    "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json", params=params, headers=headers)

soup = BeautifulSoup(html.content, "html.parser")

print(soup.find("content"))

with open('comments.json', 'w') as fp:
    soup.find()
    fp.write(json.dumps(soup))
