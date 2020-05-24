from scrapy.item import Item, Field


class CommentItem(Item):
    """ 
    댓글 모델 
    """
    contents = Field()
    like = Field()
    date = Field()
    title = Field()
    no = Field()
