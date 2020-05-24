import requests
import lxml
import json
import re
from bs4 import BeautifulSoup

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

    piece = {}
    piece["title"] = title
    piece["titleId"] = titleId
    piece["weekday"] = weekday

    data.append(piece)

with open("webtoonList.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
