import ast
import scrapy
import json
from datetime import datetime
from comic.items import CommentItem
from pymongo import MongoClient


class CommentSpider(scrapy.Spider):
    name = "comment"
    start_urls = [
        "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"]
    headers = {
        "referer": "https://comic.naver.com/comment/comment.nhn?titleId=570503&no=304"
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.CommentPipeline': 600
        }
    }

    def __init__(self):
        self.db = MongoClient()["comic"]

    def start_requests(self):
        episodes = self.db["episodes"].find()
        for episode in episodes:
            episodeNo = episode['episodeNo']
            titleId = episode["titleId"]
            i = 5  # comment amount (max: 100)
            params = {"ticket": "comic", "pool": "cbox3", "sort": "best",
                      "lang": "ko", "objectId": str(titleId)+"_"+str(episodeNo), "pageSize": str(i)}
            for url in self.start_urls:
                request = scrapy.FormRequest(
                    url=url, headers=self.headers, method="GET", formdata=params)
                request.meta["item"] = episode['_id']
                yield request

    def parse(self, response):
        comments = response.body.decode('utf-8')
        comments = comments.split('"commentList":')[1]
        comments = comments.split(',"pageModel"')[0]
        comments = json.loads(comments)

        for comment in comments:
            dt_string = comment["modTime"]
            date = datetime.strptime(
                dt_string, "%Y-%m-%dT%H:%M:%S%z")

            item = CommentItem()
            item["contents"] = comment["contents"]
            item["like"] = comment["sympathyCount"]-comment["antipathyCount"]
            item["date"] = date
            item["episodeId"] = response.meta["item"]
            yield item
