import ast
import scrapy
import json
import re
from datetime import datetime
from comic.items import WebtoonItem


class WebtoonSpider(scrapy.Spider):
    name = "webtoon"
    start_urls = ["https://comic.naver.com/webtoon/weekday.nhn"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'comic.pipelines.WebtoonPipeline': 400
        }
    }

    def parse(self, response):
        aTags = response.css("div.thumb > a")
        for aTag in aTags:

            # title
            title = aTag.xpath(".//img/@title").get()

            # titleId
            link = aTag.attrib["href"]
            titleId = int(re.search("=(.*?)&", link).group(1))

            # dayrank
            dayrank = []
            for i in response.xpath(f"//div[@class='thumb']/a/img[@title='{title}']/.."):
                el = {}
                d = i.attrib['href'].split("=")[2]
                el["day"] = d
                r = i.attrib['onclick'].split("'")[5]
                el["rank"] = int(r)
                dayrank.append(el)

            item = WebtoonItem()
            item["title"] = title
            item["titleId"] = titleId
            item["dayrank"] = dayrank

            request = scrapy.Request(
                f"https://comic.naver.com/webtoon/list.nhn?titleId={titleId}", self.parse_list)
            request.meta['item'] = item
            yield request

    def parse_list(self, response):
        item = response.meta['item']

        # totalNo
        link = response.css("td.title > a::attr(href)").get()
        no = int(re.search("no=(.*?)&", link).group(1))

        # genre
        g_str = response.css("span.genre::text").get()
        g_list = g_str.split(", ")
        genre = (g_list[0], g_list[1])

        # age
        a_str = response.css("span.age::text").get().strip()
        if a_str == "전체연령가":
            age = 0
        elif a_str == "12세 이용가":
            age = 12
        elif a_str == "15세 이용가":
            age = 15
        else:
            age = 19

        item["totalNo"] = no
        item["genre"] = genre
        item["age"] = age

        request = scrapy.Request(
            f"https://comic.naver.com/webtoon/list.nhn?titleId={item['titleId']}&page=200", self.get_period)
        request.meta['item'] = item
        yield request

    def get_period(self, response):
        item = response.meta['item']

        list_length = len(response.css("td.num"))
        d_text = response.css("td.num::text").getall()[list_length-1]

        date = datetime.strptime(d_text, "%Y.%m.%d")

        item["startDate"] = date

        request = scrapy.Request(
            f"https://comic.like.naver.com/likeIt/likeItContent.jsonp?serviceId=COMIC&contentsId={item['titleId']}", self.parse_likeCount)
        request.meta['item'] = item
        yield request

    def parse_likeCount(self, response):
        item = response.meta['item']

        likeIt = response.body.decode('utf-8')
        likeIt = likeIt.split('likeItCount":')[1]
        likeIt = int(likeIt.split(',"serviceName')[0])

        item['likeIt'] = likeIt

        yield item
