import ast
import scrapy
import json
import re
from datetime import datetime
from comic.items import EpisodeItem
from pymongo import MongoClient
from dateutil.relativedelta import relativedelta


class EpisodeSpider(scrapy.Spider):
    name = "episode"
    start_urls = ["https://comic.naver.com/webtoon/list.nhn"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.EpisodePipeline': 500
        }
    }

    def __init__(self):
        self.db = MongoClient()["comic"]

    def start_requests(self):
        webtoons = self.db["webtoons"].find()
        for webtoon in webtoons:
            titleId = webtoon['titleId']
            params = {"titleId": str(titleId)}
            for url in self.start_urls:
                yield scrapy.FormRequest(
                    url=url, method="GET", formdata=params)

    def parse(self, response):
        dates = response.css("td.num::text").getall()
        width = response.css("span.star em::attr(style)").getall()
        no_list = response.css("td.title > a::attr(href)").getall()

        titleId = int(response.request.url.split("=")[1])

        for i in range(len(dates)):
            updateDate = datetime.strptime(dates[i], "%Y.%m.%d")
            rating = float(re.search(":(.*?)%", width[i]).group(1))
            episodeNo = int(re.search("no=(.*?)&", no_list[i]).group(1))

            item = EpisodeItem()
            item["titleId"] = titleId
            item["episodeNo"] = episodeNo
            item["rating"] = rating
            item["publicOpenDate"] = updateDate

            url = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"
            headers = {
                "referer": "https://comic.naver.com/comment/comment.nhn"
            }
            params = {"ticket": "comic", "pool": "cbox3", "sort": "best",
                      "lang": "ko", "objectId": str(titleId)+"_"+str(episodeNo), "page": '1', "pageSize": '1'}
            request = scrapy.FormRequest(
                url=url, headers=headers, method="GET", formdata=params, callback=self.parse_totalComment)
            request.meta['item'] = item
            yield request

    def parse_totalComment(self, response):
        item = response.meta['item']

        comments = response.body.decode('utf-8')
        comments = comments.split('{"comment":')[1]
        totalComment = int(comments.split(',"reply":')[0])

        item["totalComment"] = totalComment

        url = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json"
        headers = {
            "referer": "https://comic.naver.com/comment/comment.nhn"
        }
        params = {"ticket": "comic", "pool": "cbox3", "sort": "new",
                  "lang": "ko", "objectId": str(item['titleId'])+"_"+str(item['episodeNo']), "page": str(totalComment), "pageSize": '1'}
        request = scrapy.FormRequest(
            url=url, headers=headers, method="GET", formdata=params, callback=self.parse_firstComment)
        request.meta['item'] = item
        yield request

    def parse_firstComment(self, response):
        item = response.meta['item']

        comments = response.body.decode('utf-8')
        comments = comments.split('modTime":"')[1]
        d_text = comments.split('","modTimeGmt')[0]
        firstCommentDate = datetime.strptime(
            d_text, "%Y-%m-%dT%H:%M:%S%z")

        item['cookieOpenDate'] = firstCommentDate
        request = scrapy.Request(
            f"https://comic.like.naver.com/likeIt/likeItContent.jsonp?serviceId=COMIC&contentsId={item['titleId']}_{item['episodeNo']}", self.parse_likeCount)
        request.meta['item'] = item
        yield request

    def parse_likeCount(self, response):
        item = response.meta['item']

        like = response.body.decode('utf-8')
        like = like.split('likeItCount":')[1]
        likeItCount = int(like.split(',"serviceName')[0])

        item['likeItCount'] = likeItCount
        yield item
