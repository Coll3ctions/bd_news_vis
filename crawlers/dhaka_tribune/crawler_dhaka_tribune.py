# -*- coding: utf-8 -*-
from lxml import html, etree
import requests
from pymongo import MongoClient
from difflib import SequenceMatcher
from dateutil import parser
import time
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import urllib

districts = ["Barisal","Bagerhat","Bandarban","Barguna","Bhola","Brahmanbaria","Bogra","Chandpur","Chittagong","Chuadanga","Comilla","Coxs Bazar","Dhaka","Dinajpur","Feni","Faridpur","Gaibandha","Gazipur","Gopalganj","Habiganj","Jessore","Jhalakati","Jamalpur","Joypurhat","Jhenaidah","Kurigram","Khulna","Khagrachari","Kustia","Kishorganj","Laxmipur","Lalmonirhat","Madaripur","Magura","Meherpur","Moulvibazar","Mymensingh","Manikgonj","Munsiganj","Narail","Narayangonj","Noakhali","Naogaon","Narsingdi","Natore","Nawabgonj","Netrokona","Nilphamari","Pabna","Panchagarh","Patuakhali","Pirojpur","Rajshahi","Rajbari","Rangamati","Rangpur","Sylhet","Shariatpur","Satkhira","Sherpur","Sirajganj","Sunamgonj","Tangail","Thakurgaon"]

DOWNLOADED_IMAGE_PATH = "dhaka_tribune_images/"

def download_photo(img_url, filename):
    file_path = "%s%s" % (DOWNLOADED_IMAGE_PATH, filename)
    downloaded_image = file(file_path, "wb")

    image_on_web = urllib.urlopen(img_url)
    while True:
        buf = image_on_web.read(65536)
        if len(buf) == 0:
            break
        downloaded_image.write(buf)
    downloaded_image.close()
    image_on_web.close()

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.bd_news
dhaka_tribunes = db.dhaka_tribunes

## Getting the total number of pages in the pagination form the first page using the last page number in the pagination
first_page = requests.get('http://www.dhakatribune.com/bangladesh')
tree_first_page = html.fromstring(first_page.content)
last_page_number = int(tree_first_page.xpath('//li[@class="pager-last last"]//a/@href')[0].split('=')[1])

count = 0
##?? Solve the first page
starting_page = 1
ending_page = last_page_number + 1
for current_page in range(starting_page, ending_page):
	print "current_page ", current_page
	paginated_news = requests.get('http://www.dhakatribune.com/bangladesh?page='+str(current_page))
	tree_paginated_news = html.fromstring(paginated_news.content)
	
	## Each page has several new links, getting the links of each article from each page
	news_links = tree_paginated_news.xpath('//h2[@class="entry-title"]//a/@href')
	news_reporters_to_be_cleaned = tree_paginated_news.xpath('//div[@class="section_name"]')
	## Dates contain a lot of ' | ' , so I am removing it, but it still contains an extra - in front of it, so I will clean it later
	news_dates = tree_paginated_news.xpath('//div[@class="section_name"]/text()')
	news_dates = [x for x in news_dates if x != ' | ']
	news_dates = map(str.strip, news_dates)
	news_orignal_tags = tree_paginated_news.xpath('//a[@class="red"]/text()')

	## Image links to download them along with each news
	news_image_links = tree_paginated_news.xpath('//div[@class="entry-thumbnail"]//a//img/@src')

	print "news_links ", news_links
	print "news_dates " , news_dates
	print "news_orignal_tags " , news_orignal_tags
	print "news_image_links ", news_image_links

	news_reporters = list()
	for current_uncleaned_reporter in news_reporters_to_be_cleaned:
		rough_string = tostring(current_uncleaned_reporter, 'utf-8', method="xml")
		#print "rough_string ", rough_string
		g = html.fromstring(rough_string)
		gs = g.xpath('//span[@class="author"]')
		if len(gs) > 0:
			#print "gs ", tostring(gs[0], 'utf-8', method="xml")
			gss = html.fromstring(tostring(gs[0], 'utf-8', method="xml"))
			rep = gss.xpath('//a/text()')
			if len(rep) < 1:
				rep = ""
			else:
				rep = rep[0]
			#print rep[0]
		else:
			rep = ""
		news_reporters.append(rep)
	print "news_reporter ", news_reporters
	for i in range(len(news_links)):
		print "current_page ", current_page
		news_link = news_links[i]
		if news_link == "http://www.dhakatribune.com/":
			continue
		print "news_link ", news_link
		news_page = requests.get(news_link)
		tree_news_page = html.fromstring(news_page.content)
		news_date = news_dates[i][2:]
		news_date = parser.parse(news_date)
		print "news_date", news_date
		news_headline = tree_news_page.xpath('//h2[@class="article-title"]/text()')[0].strip()
		print "news_headline ", news_headline
		### Remember we are taking all unidentified news as national, but they can be news from Dhaka too
		news_reporter_location = news_reporters[i]
		print "news_reporter_location ", news_reporter_location
		if news_reporter_location == "":
			news_reporter = ""
			news_location = "National"
			print "news_reporter ", news_reporter
			print "news_location ", news_location
		else:
			news_reporter_location = news_reporter_location.split(',')
			if len(news_reporter_location) < 2:
				news_reporter = news_reporter_location[0].strip()
				news_location = "National"
				print "news_reporter ", news_reporter
				print "news_location ", news_location
			else:
				news_reporter = news_reporter_location[0].strip()
				news_location = news_reporter_location[1].strip()
				print "news_reporter ", news_reporter
				for district in districts:
					ratio = SequenceMatcher(None, news_location.lower(), district.lower()).ratio()
					## ratio = SequenceMatcher(None, "Coxs Bazar", "Cox\xc3\xa2\xc2\x80\xc2\x99s Bazar").ratio() = 0.769
					if ratio > 0.75:
						news_location = district
				print "news_location ", news_location

		news = tree_news_page.xpath('//div[@class="span6 article-content"]')
		if len(news) < 1:
			continue
		else:
			news_html = html.fromstring(tostring(news[0], 'utf-8', method="xml"))
			## Some strange unicode characters appear in the news text while crawling, I am removing them
			u = u'Â'
			u2 = u'â'
			# print u
			news_text = news_html.text_content().replace(u,"").replace(u2,"")
			print "news_text ", news_text

		##?? Could not Download the images, the images can not be opened after download
		# ## downloading the related image using the news link
		# news_image_link = news_image_links[i]
		# news_image_link = "http://www.dhakatribune.com"+news_image_link
		# news_image_filename = news_date.strftime('%Y-%m-%d')+news_headline.replace(" ","-")+".jpg"
		# news_image_filename.replace(",","")
		# download_photo(news_image_link,news_image_filename)
		# #urllib.urlretrieve(news_image_link, "dhaka_tribune_images/"+news_image_filename)

		## Initially all of them are null, we will assign this using machine learning
		news_original_tag = news_orignal_tags[i].lower()
		## is_negative inititated as true, when we can not find any negative keyword then it will be changed into false
		is_negative = True
		

		keyword_crime = ["rape","charge","murder","militant","robber","gunfight","blast","torture","bomb","grenade","abduct","suicide","attacked","remand","autopsy","burn","behead","death","explosive","grenade","outlaw","protest","ringleader","body","gut","shibir","mug","jmb","beaten","sexual","harass","infight","yaba","drug","clash","warrant","lynch","held","dowry","confess","housewife","untraced","loot","chase","bullet","eyewitness","terrorist","disappearance","raid","firearm","shootout","suspect","arrest","acid","miscreant","sentenced","stab","altercation","weapon","severed","bust","threat","skirmish","crack"]

		keyword_common_accident_crime = ["fire","injur","body","deceased","explod","kill"]

		keyword_accident=["electrocut","ram","colli","crash","accident","collapse","douse","plunge","drown","cylinder","crush","engulf","capsize","derail"]

		if news_original_tag.lower() == "crime":
			news_given_tag = news_original_tag.lower()
		else:
			if any(x in news_text for x in keyword_common_accident_crime):
				if any(x in news_text for x in keyword_accident):
					news_given_tag = 'accident'
				elif any(x in news_text for x in keyword_crime):
					news_given_tag = 'crime'
				else:
					news_given_tag = 'postive'
					is_negative = False
			elif any(x in news_text for x in keyword_accident):
				news_given_tag = 'accident'
			elif any(x in news_text for x in keyword_crime):
				news_given_tag = 'crime'
			else:
				news_given_tag = 'positive'
				is_negative = False
		print "news_original_tag ", news_original_tag
		print "is_negative ",is_negative
		print "news_given_tag ", news_given_tag
		
		doc = {}
		doc["news_date"] = news_date
		doc["news_link"] = news_link
		doc["news_headline"] = news_headline
		doc["news_reporter"] = news_reporter
		doc["news_location"] = news_location
		doc["news_text"] = news_text
		doc["news_original_tag"] = news_original_tag
		doc["news_given_tag"] = news_given_tag
		doc["is_negative"] = is_negative
		##?? Could not manage to download the images properly
		## Keeping the news image link an array as there can be multiple images in a news in future
		#doc["news_image_links"] = list([news_image_link])
		#doc["news_image_filename"] = news_image_filename
		current_mongo_insert_id = dhaka_tribunes.insert_one(doc).inserted_id 
		count += 1
		print "Current News Count ", count
		#time.sleep(1)

# ## Double key word = [["shot","dead"],["body","found","recover"],["death","threat"]]