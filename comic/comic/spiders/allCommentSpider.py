import ast
import scrapy
import json
from datetime import datetime
from comic.items import CommentItem
from pymongo import MongoClient


class CommentSpider(scrapy.Spider):
    name = "allComment"
    start_urls = [
        "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"]
    headers = {
        "referer": "https://comic.naver.com/comment/comment.nhn"
    }
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.allCommentPipeline': 700
        }
    }

    def __init__(self):
        self.db = MongoClient()["comic"]

    def start_requests(self):
        episodes = self.db["episodes"].find({'titleId': 651673})  # 유미의 세포들
        for episode in episodes:
            episodeNo = episode['episodeNo']
            titleId = episode["titleId"]
            totalComment = episode["totalComment"]
            i = 100  # comment amount (max: 100)

            for p in range(1, int(totalComment/100)+2):
                params = {"ticket": "comic", "pool": "cbox3", "sort": "new",
                          "lang": "ko", "objectId": str(titleId)+"_"+str(episodeNo), "pageSize": str(i), "page": str(p)}
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
