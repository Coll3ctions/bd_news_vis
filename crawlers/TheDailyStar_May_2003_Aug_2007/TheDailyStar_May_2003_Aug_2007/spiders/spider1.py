import scrapy

from TheDailyStar_May_2003_Aug_2007.items import NewsVisItem
from datetime import date, timedelta
import parsedatetime as pdt


class Spider1(scrapy.Spider):
	name = "one"
	allowed_domains = ["thedailystar.net"]

	d1 = date(2003, 05, 26)
	d2 = date(2007, 08, 14)

	delta = d2 - d1
	links = []
	for i in range(delta.days + 1):
		cdate = d1 + timedelta(days=i)
		digits = (str(cdate)).split('-')
		links.append("http://archive.thedailystar.net/" + digits[0] + '/' + digits[1] + '/' + digits[2] + '/index.htm')
	
	start_urls = links

	def parse(self, response):
		for href in response.css('a[class="mainheadlink2"]::attr("href")'):
			url = response.urljoin(href.extract())
			yield scrapy.Request(url, callback=self.parse_dir_contents)

	def parse_dir_contents(self, response):
		for sel in response.xpath('//body'):
			item = NewsVisItem()
			item['headline'] = sel.xpath('//font[@class = "mainheadlink"]/text()').extract()
			item['link'] = response.url
			item['tag'] = sel.xpath('//body//font[@class = "newspath"]/text()').extract()
			date_string = sel.xpath('//body//td[@class = "updatetime"]/font/text()').extract()
			item['date'] = ("%s" % (pdt.Calendar().parseDT(date_string[0]))[0]).split(" ")[0]
			item['lastModified'] = None

			rprtr_lctn_elem = sel.xpath('//body//font[@class = "byline"]/text()').extract()
			
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


			resp = [sel.xpath('//body//td[@class = "newsdetails"]/text()').extract(), 
					sel.xpath('//body//td[@class = "newsdetails"]/p/text()').extract()
					]
					

			item['newsBody'] = resp[1]
			for elem in resp[0]:
				item['newsBody'].insert(0, elem)

			yield item