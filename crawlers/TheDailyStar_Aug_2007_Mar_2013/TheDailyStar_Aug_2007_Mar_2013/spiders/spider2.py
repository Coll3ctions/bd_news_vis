import scrapy

from TheDailyStar_Aug_2007_Mar_2013.items import NewsVisItem
from datetime import date, timedelta
import datetime


class Spider1(scrapy.Spider):
	name = "two"
	allowed_domains = ["thedailystar.net"]

	d1 = date(2007, 8, 15)
	d2 = date(2013, 12, 16)

	delta = d2 - d1
	links = []
	for i in range(delta.days + 1):
		cdate = d1 + timedelta(days=i)
		links.append("http://archive.thedailystar.net/newDesign/archive.php?date=" + str(cdate))
	
	start_urls = links

	def parse(self, response):
		for href in response.css('div[class="leftcolumn txt txt2"] > div[class="newes"] > fieldset > h2 > a::attr("href")'):
			url = response.urljoin(href.extract())
			yield scrapy.Request(url, callback=self.parse_dir_contents)

	def parse_dir_contents(self, response):
		for sel in response.xpath('//div[@class="conarea nobdr"]'):
			item = NewsVisItem()
			heading1 = sel.xpath('fieldset/h1/text()').extract()
			heading2 = sel.xpath('fieldset/h2/text()').extract()
			heading3 = sel.xpath('fieldset/h3/text()').extract()

			item['headline'] = heading1 + heading2 + heading3
			item['link'] = response.url
			item['tag'] = sel.xpath('span[@class="newsdate"]/div/text()').extract()
			date_string = sel.xpath('span[@class="newsdate"]/text()').extract()[0].strip()
			item['date'] = datetime.datetime.strptime(str(date_string),"%A, %B %d, %Y").strftime("%Y-%m-%d")
			item['lastModified'] = None

			rprtr_lctn_elem = sel.xpath('//span[@class="byline"]/text()').extract()
			
			if not rprtr_lctn_elem:
				item['reporter'] = None
				item['location'] = None				
			else:
				rprtr_lctn = rprtr_lctn_elem[0].split(',')
				if len(rprtr_lctn) > 1:
					item['reporter'] = rprtr_lctn[0]
					item['location'] = rprtr_lctn[-1]
				else:
					item['reporter'] = rprtr_lctn[0]
					item['location'] = None


			resp = [sel.xpath('p/text()').extract()
					]
					

			item['newsBody'] = resp[0]
			#for elem in resp[0]:
			#	item['newsBody'].insert(0, elem)

			yield item