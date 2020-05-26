from scrapy.item import Item, Field


class WebtoonItem(Item):
    title = Field()
    titleId = Field()
    dayrank = Field()
    likeIt = Field()
    totalNo = Field()
    genre = Field()
    age = Field()
    startDate = Field()


class EpisodeItem(Item):
    titleId = Field()
    episodeNo = Field()
    rating = Field()
    likeItCount = Field()
    publicOpenDate = Field()
    cookieOpenDate = Field()
    totalComment = Field()


class CommentItem(Item):
    contents = Field()
    like = Field()
    date = Field()
    episodeId = Field()
