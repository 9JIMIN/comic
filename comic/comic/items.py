from scrapy.item import Item, Field


class ComicItem(Item):
    """ 
    댓글 모델 
    """
    contents = Field()
    like = Field()
    date = Field()
    objectId = Field()
