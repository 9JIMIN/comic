import requests
import lxml
import json
import re
from bs4 import BeautifulSoup
import pymongo

connection = pymongo.MongoClient('mongodb://localhost:27017')
db = connection["comic"]

html = requests.get(
    "https://comic.naver.com/webtoon/weekday.nhn")

soup = BeautifulSoup(html.content, "lxml")

aTags = soup.select("div.thumb > a")
data = []
for aTag in aTags:
    link = aTag.attrs["href"]

    titleId = re.search("=(.*?)&", link).group(1)
    weekday = link.split("=")[2]
    title = aTag.img.attrs["title"]

    html = requests.get(
        f"https://comic.naver.com/webtoon/list.nhn?titleId={titleId}&weekday={weekday}")
    soup = BeautifulSoup(html.content, "lxml")
    link = soup.select_one("td.title > a").attrs["href"]
    no = re.search("no=(.*?)&", link).group(1)
    piece = {}
    piece["title"] = title
    piece["titleId"] = titleId
    piece["weekday"] = weekday
    piece["no"] = no

    data.append(piece)


db["webtoons"].insert_many(data)
