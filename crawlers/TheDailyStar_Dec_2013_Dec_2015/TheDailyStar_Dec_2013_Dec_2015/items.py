# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsVisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	headline = scrapy.Field()
	link = scrapy.Field()
	tag = scrapy.Field()	
	date = scrapy.Field()
	lastModified = scrapy.Field()	
	reporter = scrapy.Field()
	location = scrapy.Field()
	newsBody = scrapy.Field()
	
