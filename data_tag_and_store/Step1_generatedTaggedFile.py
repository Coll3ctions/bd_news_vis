# Khalid Jawed
import numpy as n
import os
import subprocess
import time
import sys

basename = "java -mx600m -cp ../stanford-ner-2014-06-16/stanford-ner.jar edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier ../stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz -textFile "

for root, dirs, files in os.walk("../test_data/dailystarnew"):
	for file in files:
		if file.endswith(".txt"):
			txtfile = os.path.join(root, file)
			parsedFile = txtfile[0:-4] + "_parsed.txt"
			cmdline = basename + txtfile + " > " + parsedFile + "\n"
			BASimProcess = subprocess.Popen(cmdline, shell=True)
			BASimProcess.wait()
