bd_news_vis collaboration

### Team Division
- Saquib (analysis - distribution fitting, PCA, DTW)
- Khalid (analysis - distribution fitting + tagging)
- Mehrab (analysis, data collection from other sources (weather shocks, climate, policies in heath and education))
- Mishuk (back-end, analysis)
- Salman (web front end and back end, ngram viewer)
- Tamzid (facebook graph api -- internet reach in different districts, interest topics of different people)

### Todo list
- ~~daily star crawled text (mishuk, salman)~~
  - images to be downloaded
  - tags to be machine learned
- ~~dhaka tribune crawled text (mishuk)~~
  - images to be downloaded
- prothom alo english version crawled text (mishuk)
- ~~NER tagging (mishuk + khalid)~~
  - ~~interface with MongoDB~~
- d3plus visualization (salman, saquib)
  - improve on existing code from zeeshan (kolpokoushol student)
  - ~~ngram viewer type interface~~
  - network diagrams (show relationship between entities)
- server space (mishuk + saquib)
  - ~~AWS account for server space~~
  - for now, mit.edu server. later AWS if needed.
- Marketing (everyone)
  - prothom alo news
  - facebook page
  - after product launch
- Brand name
  - a group of data volunteers?

### Issues (add more to keep track)
- ~~xpath parsing not returning 0 or null results (mishuk)~~
- ~~scrapy crawling not working with xpath (salman)~~
- d3plus map not showing full region (saquib)

### Data analysis methods (ideas)
- PCA on entity-location matrix (locations are columns/dimensions)
  - who is going where, are people following each other around (for elections)
  - do MPs talk about their area in newspaper?
- DTW (dynamic time warping) on time series of popularity/attention of entities.
  - can we track 
- Devise a metric for popularity decay that takes account of
  - width of waves (w_1, ..., w_n)
  - period between waves (T_1, ..., T_(n-1))
  - amplitude and/or area under the curve of a particular pulse (A_1, ..., A_n)
  - Reward function for frequent show-ups of entities.
  - We may need to sub-sample the time series to make the above quantities meaningful.
- Gaussian Distribution (a standard one for khaleda or hasina). 
- What is the functional shape that describes a newspaper memory. (sum of a few functions that can generalize to any entity news).
  - we can try to fit a power law by binning time. See if newspapers have similar exponents
  - say, a weibull distribution describes rare events. then we can express it as a sum of the same distribution for popular entities.
- rank distribution (sigmoid function) (bursty-ness)
- Come up with a metric for comparing newspapers (giving a formal structure to previous newspaper area coverage work)
  - This metric can take account of mutual information overlap between two newspapers based on an ensemble of entities and their relative coverage.
  - entity in this case may mean location or person.

### Further ideas:
- decay rate of public memory (characteristic rate for every country?)
- does climate change correlate with news trend?
- policy making data available? any correlation with public memory decay rate?
- network analysis between entities
- Fulfillment of promises by polittical leaders (maybe far fetched but still worth exploring)
- comparing newspaper biases
  - sentiment analysis can be augmented with frequency of bias terms
- automatic crawler (mishuk and salman)
- how to find a metric of transparency? control dataset?
- can we use grammar analysis or regx parser or similar tools to understand road accident locations
- investment opportunities based on location based news
- news trend and correlation with economic growth
- sentiment analysis and news mention can be analyzed to see if they have correlation with economic metrics.

### further further ideas
- surface temperature, rainfall viz for district wise.
- blog topics
- facebook feeds (graph api)

### Possible Journals: 
- AEP
- APS
- Arxiv

### Result Dump
URL for write up: https://www.sharelatex.com/project/548c9da8f76b211010f38142

### To run the crawler

- Install the required python modules
```
pip install newspaper pymongo
```
- Go to python and download the nltk corpora using following ocmmands:
```
import nltk
nltk.download('punkt')
nltk.download('all')
```
- Now install the Stanford NER tagger:
```
cd $HOME

# Update / Install NLTK
pip install -U nltk

# Download the Stanford NLP tools
wget http://nlp.stanford.edu/software/stanford-ner-2015-04-20.zip
wget http://nlp.stanford.edu/software/stanford-postagger-full-2015-04-20.zip
wget http://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip
# Extract the zip file.
unzip stanford-ner-2015-04-20.zip 
unzip stanford-parser-full-2015-04-20.zip 
unzip stanford-postagger-full-2015-04-20.zip
```
- Copy and add the follwing paths to `.bashrc` file using this command `nano ~/.bashrc`:
```
export STANFORDTOOLSDIR=$HOME

export CLASSPATH=$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/stanford-postagger.jar:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/stanford-ner.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser.jar:$STANFORDTOOLSDIR/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar

export STANFORD_MODELS=$STANFORDTOOLSDIR/stanford-postagger-full-2015-04-20/models:$STANFORDTOOLSDIR/stanford-ner-2015-04-20/classifiers
```
[Source: Stackoverflow](http://stackoverflow.com/questions/13883277/stanford-parser-and-nltk/34112695#34112695)

- Install Java 8 (oracle-jdk-8)
```
java -version
sudo apt-get install python-software-properties
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer
```
[Source: Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-ubuntu-with-apt-get)
- Install mongodb:
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.com/apt/ubuntu trusty/mongodb-enterprise/stable multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise.list
sudo apt-get update
sudo apt-get install -y mongodb-enterprise
```
[Source: MongoDB](https://docs.mongodb.org/manual/tutorial/install-mongodb-enterprise-on-ubuntu/)
#### Points to be noted for Stanford NER tagger:
- Sometimes it confuses one single entity into multiple entities, e.g. "Lt Colonel Shahidur Rahman", "Shahidur Rahman", "Shahidur" are recognized as different entities
- It mixes up the organizations and persons frequently
- So far I haven't seen to it to identify the Taka amounts as money in any article

### Mongo Data structure for the news:

- _id : `ObjectID`
- newspaper_name: `String` e.g. "Dhaka Tribune", "The Daily Star"
- newspaper_url: `URL` e.g. "http://www.thedailystar.net"
- news_headline : `String` e.g. "They all care about democracy"
- news_publish_date: `ISODate`
- news_url: `URL` e.g. "http://www.thedailystar.net/frontpage/they-all-care-about-democracy-197176"
- news_original_tags : `list of Lowercase String` e.g. "bangladesh"
- news_naive_tags: `list of Lowercase Strings` e.g. \["crime"\]
- news_ml_tags : `list of Strings` e.g. \["violence", "domestic", "crime"\]
- news_reporters : `List of Strings` e.g. ["Captain Bangladesh", "Captain America"]
- news_location: `String` e.g. "Narail" (This is a district name. To keep the district name same we can use the same `districts` list provided below. For dhaka tribune, all the dhaka news and national news are marked as "national", other wise tried to find the location whule crawling using thier tag. Still we have to find and verifiy the locations using NER tagging)
- news_text: `String` (I am keeping it as an utf text with all the newlines and quotation marks)
- is_negative : `boolean`
- news_image_urls : `list of URLs`
- news_crawled_date: `ISODate`
- news_keywords: `list of String`
- news_ner_tags: {locations:\[list of string\], persons:\[list of string\], organizations:\[list of string\], moneys:\[list of amounts\], percents:\[list of percents\], dates:\[list of dates\], times:\[list of times\],locations_unique:\[list of string\], persons_unique:\[list of string\], organizations_unique:\[list of string\], moneys_unique:\[list of amounts\], percents_unique:\[list of percents\], dates_unique:\[list of dates\], times_unique:\[list of times\]

}

A python list of districts:

```
districts = ["Barisal","Bagerhat","Bandarban","Barguna","Bhola","Brahmanbaria","Bogra","Chandpur","Chapainawabganj","Chittagong","Chuadanga","Comilla","Coxs Bazar","Dhaka","Dinajpur","Feni","Faridpur","Gaibandha","Gazipur","Gopalganj","Habiganj","Jessore","Jhalokati","Jamalpur","Joypurhat","Jhenaidah","Kurigram","Khulna","Khagrachhari","Kushtia","Kishoreganj","Lakshmipur","Lalmonirhat","Madaripur","Magura","Meherpur","Moulvibazar","Mymensingh","Manikganj","Munshiganj","Narail","Narayanganj","Noakhali","Naogaon","Narsingdi","Natore","Netrokona","Nilphamari","Pabna","Panchagarh","Patuakhali","Pirojpur","Rajshahi","Rajbari","Rangamati","Rangpur","Sylhet","Shariatpur","Satkhira","Sherpur","Sirajganj","Sunamgonj","Tangail","Thakurgaon"]
```
### Installing Elasticsearch and Kibana

#### Mac:
Use this [tutorial](https://gist.github.com/squarism/8fa9cdd7d6b36c9fcb45) to install Elasticsearch and Kibana and Nginx in Mac. You do not need to install logstash.

####Ubuntu:
Use this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elk-stack-on-ubuntu-14-04) to install Elasticearch, Kibana and Nginx. Again, we do not need logstash.

#### To check if the database is up and running:
```
curl -X GET 'http://localhost:9200'
```

#### To check the available databases and their size:
```
curl 'localhost:9200/_cat/indices?v'
```
