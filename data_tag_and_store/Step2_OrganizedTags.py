# Khalid Jawed
import numpy as n
import os
import subprocess
import time
import sys

# Each new item in parsed file is separated by 'delims'
delims = "//O //O //O //O //O //O"
delimsLocal = ["/ORGANIZATION", "/PERSON", "/LOCATION"]

organizedFile = "OrganizedFile.csv"
f = open(organizedFile, 'w')
f.write("Year, Month, Day, NewsID, Entity, Type\n")

for root, dirs, files in os.walk("../test_data/dailystarnew"):
	for file in files:
		if file.endswith("_parsed.txt"):

			# Figure out date
			strippedFile = file
			year = strippedFile[0:4]
			mo = strippedFile[5:7]
			day = strippedFile[8:10]

			# Read the file contents
			parsedFile = os.path.join(root, file)
			fileContents = open(parsedFile, 'r').read()

			
			# Separate into news
			location = 0
			NewsID = 0
			while True:
				NewsID = NewsID + 1
				location0 = location
				location = fileContents.find(delims, location + 1)
				if location == -1: break
				newsContent = fileContents[location0:location-1]
				
				words = newsContent.split()

				# Search for organizations
				for k in range(len(words)):
					for kk in range(len(delimsLocal)):
						delimLen = len(delimsLocal[kk])
						if words[k].endswith(delimsLocal[kk]):
							entityName = words[k][0:-delimLen]
							csvString = year+"," + mo + "," + day + "," + \
								str(NewsID) + " , " + entityName + "," + \
								delimsLocal[kk][1::]
							f.write(csvString + "\n")
			
f.close()
