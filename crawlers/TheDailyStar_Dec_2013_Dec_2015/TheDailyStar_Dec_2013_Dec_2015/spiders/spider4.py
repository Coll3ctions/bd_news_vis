import scrapy

from TheDailyStar_Dec_2013_Dec_2015.items import NewsVisItem
from datetime import date, timedelta


class Spider4(scrapy.Spider):
	name = "four"
	allowed_domains = ["thedailystar.net"]

	d1 = date(2013, 12, 17)
	d2 = date(2015, 12, 31)

	delta = d2 - d1
	links = []
	for i in range(delta.days + 1):
		cdate = d1 + timedelta(days=i)
		links.append("http://www.thedailystar.net/newspaper?date=" + str(cdate))
	
	start_urls = links

	def parse(self, response):
		for href in response.css("div[class = 'panel-pane pane-news-col no-title block'] > div > div > div[class = 'three-33'] > ul > li > div > h5 > a::attr('href')"):
			url = response.urljoin(href.extract())
			yield scrapy.Request(url, callback=self.parse_dir_contents)

	def parse_dir_contents(self, response):
		for sel in response.xpath('//div[@class="content"]'):
			item = NewsVisItem()
			item['headline'] = sel.xpath('//div[@class="panel-pane pane-views-panes pane-news-details-panel-pane-10 no-title block"]/div/h1/text()').extract()
			item['link'] = response.url
			item['tag'] = None
			item['date'] = sel.xpath('//div[@class="panel-pane pane-views-panes pane-news-details-panel-pane-1 no-title block"]/div/div/text()').extract()[0].split('/')[0] 
			item['lastModified'] = sel.xpath('//div[@class="panel-pane pane-views-panes pane-news-details-panel-pane-1 no-title block"]/div/div/text()').extract()[0].split('/')[1]

########## Shitty code starts				
			if len(sel.xpath('//div[contains(@class, "author-name")]/span')) == 0:
				a = sel.xpath('//div[contains(@class, "author-name")]/span/a/text()').extract()
				if len(a) > 0:
					b = a[0].split(", ")
					item['reporter'] = b[0]
					if len(b) > 1:
						item['location'] = b[1]
					else:
						item['location'] = None
			else:
				a = sel.xpath('//div[contains(@class, "author-name")]/span/text()').extract()
				if len(a) > 0:
					b = a[0].split(", ")
					item['reporter'] = b[0]
					if len(b) > 1:
						item['location'] = b[1]
					else:
						item['location'] = None
########## Shitty code ends

			resp = [sel.xpath('//div[@class="field-body view-mode-teaser"]/p/text()').extract(),
					sel.xpath('//div[@class="field-body view-mode-teaser"]/p/span/text()').extract(),
					sel.xpath('//div[@class="field-body view-mode-teaser"]/div/p/text()').extract(),
					sel.xpath('//div[@class="field-body view-mode-teaser"]/div/text()').extract()
					]

			for r in resp:
				if len(r) != 0:
					item['newsBody'] = r
					break

			yield item
