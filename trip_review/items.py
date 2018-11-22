# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TripReviewItem(scrapy.Item):
    hotel_name = scrapy.Field()
    rev_bub = scrapy.Field()
    rev_date = scrapy.Field()
    rev_header = scrapy.Field()
    rev_stayed = scrapy.Field()
    rev_text = scrapy.Field()
    member = scrapy.Field()
    age = scrapy.Field()
    sex = scrapy.Field()
    member_from = scrapy.Field()
