import ast
import scrapy
import json
from datetime import datetime
from comic.items import CommentItem


class CommentSpider(scrapy.Spider):
    name = "comment"

    start_urls = [
        "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=comic&pool=cbox3&lang=ko&objectId=570503_304&pageSize=5"]

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "referer": "https://comic.naver.com/comment/comment.nhn?titleId=570503&no=304"
    }

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, headers=self.headers)

    def parse(self, response):
        comments = response.body.decode('utf-8')
        comments = comments.split('"commentList":')[1]
        comments = comments.split(',"pageModel"')[0]

        comments = json.loads(comments)

        for comment in comments:
            item = CommentItem()
            item["contents"] = comment["contents"]
            item["like"] = comment["sympathyCount"]

            dt_string = comment["modTime"]

            date = datetime.strptime(
                dt_string, "%Y-%m-%dT%H:%M:%S%z")
            item["date"] = date

            item["objectId"] = comment["objectId"]
            yield item
