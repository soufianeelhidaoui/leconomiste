# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class LeconomisteItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    category = scrapy.Field()
    author = scrapy.Field()
    date_published = scrapy.Field()
    image_url = scrapy.Field()
    content = scrapy.Field()