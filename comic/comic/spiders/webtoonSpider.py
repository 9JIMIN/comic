import ast
import scrapy
import json
import re
from datetime import datetime
from comic.items import WebtoonItem
from pymongo import MongoClient


class WebtoonSpider(scrapy.Spider):
    name = "webtoon"
    start_urls = ["https://comic.naver.com/webtoon/weekday.nhn"]
    db = MongoClient()["comic"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.WebtoonPipeline': 400
        }
    }

    def parse(self, response):
        aTags = response.css("div.thumb > a")
        for aTag in aTags:
            link = aTag.attrib["href"]
            titleId = re.search("=(.*?)&", link).group(1)
            weekday = link.split("=")[2]
            title = aTag.xpath(".//img/@title").get()

            item = WebtoonItem()
            item["title"] = title
            item["titleId"] = int(titleId)
            item["weekday"] = weekday
            request = scrapy.Request(
                f"https://comic.naver.com/webtoon/list.nhn?titleId={titleId}&weekday={weekday}", self.parse_no)
            request.meta['item'] = item
            yield request

    def parse_no(self, response):
        item = response.meta['item']
        link = response.css("td.title > a::attr(href)").get()
        no = re.search("no=(.*?)&", link).group(1)
        item["latestNo"] = int(no)
        yield item
