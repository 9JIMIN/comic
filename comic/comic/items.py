from scrapy.item import Item, Field


class CommentItem(Item):
    contents = Field()
    like = Field()
    date = Field()
    titleId = Field()
    no = Field()


class EpisodeItem(Item):
    rating = Field()
    date = Field()
    titleId = Field()
    no = Field()


class WebtoonItem(Item):
    title = Field()
    titleId = Field()
    weekday = Field()
    latestNo = Field()
