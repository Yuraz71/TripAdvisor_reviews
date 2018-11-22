# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from trip_review.items import TripReviewItem
import re


class ReviewSpider(Spider):
    name = 'review'
    start_urls = ['https://www.tripadvisor.co.uk/Hotels-g186338-London_England-Hotels.html',]

    def parse(self, response):
        # Start page with list of hotels
        # Loop for 30 hotels per page and request link within 'Next' button
        hotels = response.xpath("//div[@class='prw_rup prw_meta_hsx_responsive_listing ui_section listItem']"
                                "/div/div[@data-index]")
        # Loop for 30 hotels per page
        for hotel in hotels:
            url_detail = hotel.xpath(".//div[@class='listing_title']/a/@href").extract_first()
            url_detail = 'https://www.tripadvisor.co.uk' + url_detail
            # Request hotel detail page, call parse_detail method
            yield Request(url=url_detail, callback=self.parse_detail)

        # If exists button 'Next', request next page
        btn_next = response.xpath("//link[@rel='next']/@href").extract()[0]
        url_next = 'https://www.tripadvisor.co.uk' + btn_next
        if btn_next:
            yield Request(url=url_next, callback=self.parse)

    def parse_detail(self, response):
        # Page with hotel's description
        # Loop for 5 reviews per page, request link within 'Next' button
        reviews = response.xpath("//div[@class='review-container']")
        for review in reviews:
            try:
                url_review = review.xpath(".//div[@class='quote isNew']/a/@href").extract()[0]
            except:
                url_review = review.xpath(".//div[@class='quote']/a/@href").extract()[0]
            url_review = 'https://www.tripadvisor.co.uk' + url_review
            # Request page of particular review, call parse_review method
            yield Request(url=url_review, callback=self.parse_review)
        # If exists button 'Next', request next page of reviews
        btn_next = response.xpath("//link[@rel='next']/@href").extract()[0]
        url_next = 'https://www.tripadvisor.co.uk' + btn_next
        if btn_next:
            yield Request(url=url_next, callback=self.parse_detail)


    def parse_review(self, response):
        # Parse page of particular review for required fields according TripReviewItem model
        # Parse Member ID for request member detail page
        review_container = response.xpath("//div[@class='featured-review-container']")
        hotel_name = review_container.xpath("//div[@class='altHeadInline']/a/text()").extract()[0]

        rev_bub = ''
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_50']"): rev_bub = '5'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_45']"): rev_bub = '4,5'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_40']"): rev_bub = '4'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_35']"): rev_bub = '3,5'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_30']"): rev_bub = '3'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_25']"): rev_bub = '2,5'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_20']"): rev_bub = '2'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_15']"): rev_bub = '1,5'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_10']"): rev_bub = '1'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_05']"): rev_bub = '0,5'
        if review_container.xpath(".//span[@class='ui_bubble_rating bubble_00']"): rev_bub = '0'

        rev_date = review_container.xpath(".//span[@class='ratingDate']/@title").extract()[0]
        rev_header = review_container.xpath("//h1[@id='HEADING']/text()").extract()[0]
        try:
            rev_stayed =  review_container.xpath(".//div[@class='recommend-titleInline noRatings']/text()").extract()[0]
        except:
            rev_stayed = review_container.xpath(".//div[@class='recommend-titleInline']/text()").extract()[0]
        rev_text = ' '.join(review_container.xpath(".//span[@class='fullText ']/text()").extract())

        # Parse Member ID
        member_id = review_container.xpath("//div[@class='prw_rup prw_reviews_member_info_resp_sur']/div/div/@id").extract()[0]
        member_id = member_id.split('_')[1]
        member_id = member_id.split('-')[0]

        url_member = 'https://www.tripadvisor.co.uk/MemberOverlay?Mode=owa&uid=' \
                     + member_id + '&c=&fus=false&partner=false&LsoId=&metaReferer=ShowUserReviewsHotels'
        url_member = re.sub('%20+', '', url_member)

        # Request member detail page
        yield Request(url=url_member, callback=self.parse_member,
                      meta={'hotel_name': hotel_name, 'rev_bub': rev_bub, 'rev_date': rev_date, 'rev_header': rev_header,
                            'rev_stayed':rev_stayed, 'rev_text': rev_text})

    def parse_member(self, response):
        # Parse member detail page for remaining fields according TripReviewItem model
        hotel_name = response.meta['hotel_name']
        rev_bub = response.meta['rev_bub']
        rev_date = response.meta['rev_date']
        rev_header = response.meta['rev_header']
        rev_stayed = response.meta['rev_stayed']
        rev_text = response.meta['rev_text']

        member = response.xpath('//h3/text()').extract()[0]
        try:
            description = response.xpath("//ul[@class='memberdescriptionReviewEnhancements']/li/text()")[1].extract()
        except:
            description = ''
        member_from = ''
        sex = ''
        age = ''
        if description:
            member_desc_split = description.split(' ')
            i = 0
            while i < len(member_desc_split):
                if re.search('from|From', member_desc_split[i]):
                    member_from = ' '. join(member_desc_split[i+1:len(member_desc_split)-1])
                elif re.search('man|Man|woman|Woman|male|Male|female|Female', member_desc_split[i]):
                    sex = member_desc_split[i]
                elif re.search("[0-9]+", member_desc_split[i]):
                    age = member_desc_split[i]
                i += 1

        item = TripReviewItem()
        item['hotel_name'] = hotel_name
        item['rev_bub'] = rev_bub
        item ['rev_date'] = rev_date
        item['rev_header'] = rev_header
        item['rev_stayed'] = rev_stayed
        item['rev_text'] = rev_text
        item['member'] = member
        item['member_from'] = member_from
        item['sex'] = sex
        item['age'] = age

        yield item
