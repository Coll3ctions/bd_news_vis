# -*- coding: utf-8 -*-
from lxml import html, etree
import requests
from pymongo import MongoClient
from difflib import SequenceMatcher
from dateutil import parser
import time
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import urllib
import os
from nltk.tag import StanfordNERTagger
from nltk import pos_tag
from nltk.chunk import conlltags2tree
from nltk.tree import Tree
from newspaper import Article
import datetime
from elasticsearch import Elasticsearch

## Getting the total number of pages in the pagination form the first page using the last page number in the pagination
first_page = requests.get('http://www.dhakatribune.com/bangladesh')
tree_first_page = html.fromstring(first_page.content)
last_page_number = int(tree_first_page.xpath('//li[@class="pager-last last"]//a/@href')[0].split('=')[1])

## Parameters of the crawler
count = 0
## I am never taking the 0th page, because those would be the part of the cron jobs of some the next date
starting_page = 1
ending_page = last_page_number + 1
circuit_breaker = False

## Here starts the actual crawling for Dhaka Tribune
newspaper_name = "Dhaka Tribune"
newspaper_url = "http://www.dhakatribune.com"

districts = ["Barisal","Bagerhat","Bandarban","Barguna","Bhola","Brahmanbaria","Bogra","Chandpur","Chapainawabganj","Chittagong","Chuadanga","Comilla","Coxs Bazar","Dhaka","Dinajpur","Feni","Faridpur","Gaibandha","Gazipur","Gopalganj","Habiganj","Jessore","Jhalokati","Jamalpur","Joypurhat","Jhenaidah","Kurigram","Khulna","Khagrachhari","Kushtia","Kishoreganj","Lakshmipur","Lalmonirhat","Madaripur","Magura","Meherpur","Moulvibazar","Mymensingh","Manikganj","Munshiganj","Narail","Narayanganj","Noakhali","Naogaon","Narsingdi","Natore","Netrokona","Nilphamari","Pabna","Panchagarh","Patuakhali","Pirojpur","Rajshahi","Rajbari","Rangamati","Rangpur","Sylhet","Shariatpur","Satkhira","Sherpur","Sirajganj","Sunamgonj","Tangail","Thakurgaon"]

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

## Load Elasticsearch
es = Elasticsearch()

## Setting up Stanfor NER Tagger 
## using these instructions: http://stackoverflow.com/questions/13883277/stanford-parser-and-nltk/34112695#34112695
stanford_ner_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../..', 'stanford_ner_classifiers'))
st = StanfordNERTagger("english.muc.7class.distsim.crf.ser.gz") 

## Now creating a function for tidying the entities
## using this resource: http://stackoverflow.com/questions/30664677/extract-list-of-persons-and-organizations-using-stanford-ner-tagger-in-nltk?answertab=votes#tab-top
def stanfordNE2BIO(tagged_sent):
	bio_tagged_sent = []
	prev_tag = "O"
	for token, tag in tagged_sent:
		if tag == "O": #O
			bio_tagged_sent.append((token, tag))
			prev_tag = tag
			continue
		if tag != "O" and prev_tag == "O": # Begin NE
			bio_tagged_sent.append((token, "B-"+tag))
			prev_tag = tag
		elif prev_tag != "O" and prev_tag == tag: # Inside NE
			bio_tagged_sent.append((token, "I-"+tag))
			prev_tag = tag
		elif prev_tag != "O" and prev_tag != tag: # Adjacent NE
			bio_tagged_sent.append((token, "B-"+tag))
			prev_tag = tag

	return bio_tagged_sent

def stanfordNE2tree(ne_tagged_sent):
	bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
	sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)
	sent_pos_tags = [pos for token, pos in pos_tag(sent_tokens)]

	sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(sent_tokens, sent_pos_tags, sent_ne_tags)]
	ne_tree = conlltags2tree(sent_conlltags)
	return ne_tree

def create_ner_entities_tuple(text):
	ne_tagged_sent = st.tag(text.split())
	ne_tree = stanfordNE2tree(ne_tagged_sent)
	ne_in_sent = []
	for subtree in ne_tree:
		if type(subtree) == Tree: # If subtree is a noun chunk, i.e. NE != "O"
			ne_label = subtree.label()
			ne_string = " ".join([token for token, pos in subtree.leaves()])
			ne_in_sent.append((ne_string, ne_label))
	return ne_in_sent

## Crawling through each paginated pages to collect the individual news article links
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

	## Now crawling through each individual news article of a distinct paginatated top lavel pages
	for i in range(len(news_links)):
		print
		print
		print "current page ", current_page
		print "position of this news ", i+1
		news_link = news_links[i]
		if news_link == "http://www.dhakatribune.com/":
			continue
		#### if statement to find if the news article is already in the mongodb database, if it is already there, then the crawler will stop rightaway
		# isDeletedUser = bd_news_articles.find_one({"news_url":news_link})
		# if isDeletedUser:
		# 	circuit_breaker = True
		# 	break
		print "news_link ", news_link
		news_page = requests.get(news_link)
		news_crawled_date = datetime.datetime.now()
		tree_news_page = html.fromstring(news_page.content)
		news_date = news_dates[i][2:]
		news_date = parser.parse(news_date)
		print "news_date", news_date
		news_headline = tree_news_page.xpath('//h2[@class="article-title"]/text()')
		if len(news_headline) < 1:
			time.sleep(1)
			news_headline = tree_news_page.xpath('//h2[@class="article-title"]/text()')
			if len(news_headline) < 1:
				break
			else:
				news_headline = news_headline[0].strip()
		news_headline = news_headline[0].strip()
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
				news_reporter = list()
				reps = [reporter.strip() for reporter in news_reporter_location[:-1]]
				for rep in reps:
					news_reporter.append(rep)
				news_location = news_reporter_location[-1].strip()
				print "news_reporters ", news_reporter
				for district in districts:
					ratio = SequenceMatcher(None, news_location.lower(), district.lower()).ratio()
					if ratio > 0.75:
						news_location = district
					## reason for it to be 0.75 is shown below
					## ratio = SequenceMatcher(None, "Coxs Bazar", "Cox\xc3\xa2\xc2\x80\xc2\x99s Bazar").ratio() = 0.769
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
		if news_text and news_text.strip():
			print "not blank string"
		else:
			news_text = ""
			print "blank string"
		##?? Could not Download the images, the images can not be opened after download
		# ## downloading the related image using the news link
		news_image_link = news_image_links[i]
		# news_image_link = "http://www.dhakatribune.com"+news_image_link
		# news_image_filename = news_date.strftime('%Y-%m-%d')+news_headline.replace(" ","-")+".jpg"
		# news_image_filename.replace(",","")
		# download_photo(news_image_link,news_image_filename)
		# #urllib.urlretrieve(news_image_link, "dhaka_tribune_images/"+news_image_filename)

		## Initially all of them are null, we will assign this using machine learning
		news_original_tag = news_orignal_tags[i].lower()
		## is_negative inititated as true, when we can not find any negative keyword then it will be changed into false
		is_negative = True
		
		## Using python's newspaper module to extract the news text and some very basic keywords
		try:
			article = Article(news_link)
			article.download()
			article.parse()
			article.nlp()
			news_keywords = article.keywords
			print "Article keywords ", news_keywords
			article_text = article.text
		except:
			article_text = ""
			news_keywords = []
			print "newspaper.Article Exception"
		print "article_text \n",article_text
		if article_text and article_text.strip():
			news_text = article_text

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

		## Now using Stanford's NER tagger to identify 7 different type of objects in the news article
		news_ner_tags = {}
		ner_person = []
		ner_location = []
		ner_organization = []
		ner_date = []
		ner_money = []
		ner_percent = []
		ner_time = []
		try:
			if not news_text == "":
				ner_7_class =  create_ner_entities_tuple(news_text)
				for entity in ner_7_class:
					if entity[1] == "PERSON":
						ner_person.append(entity[0])
					elif entity[1] == "LOCATION":
						ner_location.append(entity[0])
					elif entity[1] == "ORGANIZATION":
						ner_organization.append(entity[0])
					elif entity[1] == "DATE":
						ner_date.append(entity[0])
					elif entity[1] == "MONEY":
						ner_money.append(entity[0])
					elif entity[1] == "PERCENT":
						ner_percent.append(entity[0])
					elif entity[1] == "TIME":
						ner_time.append(entity[0])
				news_ner_tags['persons'] = ner_person
				news_ner_tags['locations'] = ner_location
				news_ner_tags['organizations'] = ner_organization
				news_ner_tags['dates'] = ner_date
				news_ner_tags['moneys'] = ner_money
				news_ner_tags['percents'] = ner_percent
				news_ner_tags['times'] = ner_time

				news_ner_tags['persons_unique'] = list(set(ner_person))
				news_ner_tags['locations_unique'] = list(set(ner_location))
				news_ner_tags['organizations_unique'] = list(set(ner_organization))
				news_ner_tags['dates_unique'] = list(set(ner_date))
				news_ner_tags['moneys_unique'] = list(set(ner_money))
				news_ner_tags['percents_unique'] = list(set(ner_percent))
				news_ner_tags['times_unique'] = list(set(ner_time))
			else:
				news_ner_tags['persons'] = ner_person
				news_ner_tags['locations'] = ner_location
				news_ner_tags['organizations'] = ner_organization
				news_ner_tags['dates'] = ner_date
				news_ner_tags['moneys'] = ner_money
				news_ner_tags['percents'] = ner_percent
				news_ner_tags['times'] = ner_time

				news_ner_tags['persons_unique'] = list(set(ner_person))
				news_ner_tags['locations_unique'] = list(set(ner_location))
				news_ner_tags['organizations_unique'] = list(set(ner_organization))
				news_ner_tags['dates_unique'] = list(set(ner_date))
				news_ner_tags['moneys_unique'] = list(set(ner_money))
				news_ner_tags['percents_unique'] = list(set(ner_percent))
				news_ner_tags['times_unique'] = list(set(ner_time))
		except:
			news_ner_tags['persons'] = ner_person
			news_ner_tags['locations'] = ner_location
			news_ner_tags['organizations'] = ner_organization
			news_ner_tags['dates'] = ner_date
			news_ner_tags['moneys'] = ner_money
			news_ner_tags['percents'] = ner_percent
			news_ner_tags['times'] = ner_time

			news_ner_tags['persons_unique'] = list(set(ner_person))
			news_ner_tags['locations_unique'] = list(set(ner_location))
			news_ner_tags['organizations_unique'] = list(set(ner_organization))
			news_ner_tags['dates_unique'] = list(set(ner_date))
			news_ner_tags['moneys_unique'] = list(set(ner_money))
			news_ner_tags['percents_unique'] = list(set(ner_percent))
			news_ner_tags['times_unique'] = list(set(ner_time))
			print "It was an exception for NER tagger"

		print news_ner_tags
		
		doc = {}
		doc["newspaper_name"] = newspaper_name
		doc["newspaper_url"] = newspaper_url
		doc["news_headline"] = news_headline
		doc["news_publish_date"] = news_date
		doc["news_url"] = news_link
		doc["news_original_tags"] = list([news_original_tag])
		doc["news_naive_tags"] = list([news_given_tag])
		doc["news_ml_tags"] = None
		news_reporters_list = list()
		news_reporters_list.append(news_reporter)
		doc["news_reporters"] = news_reporters_list
		doc["news_location"] = news_location
		doc["news_text"] = news_text
		doc["is_negative"] = is_negative
		##?? Could not manage to download the images properly
		## Keeping the news image link an array as there can be multiple images in a news in future
		doc["news_image_urls"] = list([news_image_link])
		#doc["news_image_filename"] = news_image_filename
		doc["news_crawled_date"] = news_crawled_date
		doc["news_keywords"] = news_keywords
		doc["news_ner_tags"] = news_ner_tags

		## inserting into elasticsearch storage
		res = es.index(index="bd_news", doc_type='article', body=doc)
		print(res['created'])
		count += 1
		print "Current page ", current_page
		print "total news inserted ", count
		#time.sleep(1)
	if circuit_breaker == True:
		break