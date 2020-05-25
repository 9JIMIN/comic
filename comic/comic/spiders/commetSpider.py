import ast
import scrapy
import json
from datetime import datetime
from comic.items import CommentItem
from pymongo import MongoClient


class CommentSpider(scrapy.Spider):
    name = "comment"
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.CommentPipeline': 600
        }
    }

    def __init__(self):
        self.start_urls = [
            "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"]
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "referer": "https://comic.naver.com/comment/comment.nhn?titleId=570503&no=304"
        }
        self.db = MongoClient()["comic"]

    def start_requests(self):
        episodes = self.db["episodes"].find()
        for episode in episodes:
            latest = episode['no']
            for i in range(latest-1, latest):
                print(i)
                params = {"ticket": "comic", "pool": "cbox3", "sort": "best",
                          "lang": "ko", "objectId": str(episode["titleId"])+"_"+str(i), "pageSize": "10"}
                for url in self.start_urls:
                    yield scrapy.FormRequest(url=url, headers=self.headers, method="GET", formdata=params)

    def parse(self, response):
        comments = response.body.decode('utf-8')
        comments = comments.split('"commentList":')[1]
        comments = comments.split(',"pageModel"')[0]

        comments = json.loads(comments)

        for comment in comments:
            item = CommentItem()
            dt_string = comment["modTime"]
            date = datetime.strptime(
                dt_string, "%Y-%m-%dT%H:%M:%S%z")

            item["contents"] = comment["contents"]
            item["like"] = comment["sympathyCount"]-comment["antipathyCount"]
            item["date"] = date
            item["titleId"] = int(comment["objectId"].split("_")[0])
            item["no"] = int(comment["objectId"].split("_")[1])
            yield item
