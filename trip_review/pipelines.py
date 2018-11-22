# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv

class TripReviewPipeline(object):
    def open_spider(self, ReviewSpider):
        self.csvfile = open("./files/reviews.csv", 'wt', encoding="UTF-8")
        self.writer = csv.writer(self.csvfile)
        
    def close_spider(self, ReviewSpider):
        self.csvfile.close()
        
    def process_item(self, reviews, ReviewSpider):
        self.writer.writerow((reviews['hotel_name'], reviews['member'], reviews['age'], reviews['sex'],
            reviews['member_from'], reviews['rev_bub'], reviews['rev_date'], reviews['rev_header'],
            reviews['rev_stayed'], reviews['rev_text']))
        reviews['hotel_name'] = reviews['member'] = reviews['age'] = reviews['sex'] = reviews['member_from'] = \
            reviews['rev_bub'] = reviews['rev_date'] = reviews['rev_header'] = reviews['rev_stayed'] = \
            reviews['rev_text'] = ''
        return reviews
