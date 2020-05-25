import ast
import scrapy
import json
import re
from datetime import datetime
from comic.items import EpisodeItem
from pymongo import MongoClient


class EpisodeSpider(scrapy.Spider):
    name = "episode"
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.EpisodePipeline': 500
        }
    }

    def __init__(self):
        self.start_urls = [
            "https://comic.naver.com/webtoon/list.nhn"]
        self.db = MongoClient()["comic"]

    def start_requests(self):
        webtoons = self.db["webtoons"].find()
        for webtoon in webtoons:
            titleId = webtoon['titleId']
            params = {"titleId": str(titleId)}
            for url in self.start_urls:
                yield scrapy.FormRequest(url=url, method="GET", formdata=params)

    def parse(self, response):
        dates = response.css("td.num::text").getall()
        width = response.css("span.star em::attr(style)").getall()
        no_list = response.css("td.title > a::attr(href)").getall()

        titleId = int(response.request.url.split("=")[1])

        for i in range(len(dates)):
            date = datetime.strptime(dates[i], "%Y.%m.%d")
            rating = float(re.search(":(.*?)%", width[i]).group(1))
            no = int(re.search("no=(.*?)&", no_list[i]).group(1))

            item = EpisodeItem()
            item["rating"] = rating
            item["date"] = date
            item["no"] = no
            item["titleId"] = titleId
            yield item
