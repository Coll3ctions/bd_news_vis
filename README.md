bd_news_vis collaboration

Team Division
- Saquib (analysis - distribution fitting)
- Khalid (analysis - distribution fitting)
- Mehrab (analysis)
- Mishuk (web front-end and back-end)
- Salman (web front end and back end)

### Todo list
- daily star crawled text (salman)
  - images to be downloaded
  - tags to be machine learned
- dhaka tribune crawled text (mishuk)
  - images to be downloaded
- prothom alo english version crawled text (mishuk)
- NER tagging (khalid, script done)
  - interface with MongoDB 
- d3plus visualization (saquib)
  - improve on existing code from zeeshan
- server space (saquib, done)
  - AWS account for server space
  - for now, mit.edu server. later AWS if needed.
- Marketing
  - prothom alo news
  - facebook page
  - after product launch
- Brand name
  - a group of data volunteers?

### Issues (add more to keep track)
- ~~xpath parsing not returning 0 or null results (mishuk)~~
- scrapy crawling not working with xpath (salman)
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

### Possible Journals: 
- AEP
- APS
- Arxiv

### Result Dump
URL for write up: https://www.sharelatex.com/project/548c9da8f76b211010f38142

### Mongo Data structure for the news:

- _id
- news_headline : `string`
- news_original_tag : `string`
- news_given_tag: `list`/`string` ?? Shouldn't we make it an array of tags? Let me know
- news_reporter : `string`
- news_date: `ISODate`
- news_link: `url`
- news_text: `string` (I am keep it as an utf text with all the newlines and quotation marks)
- news_location: `string` (This is a district name. To keep the district name same we can use the same `districts` list provided below. For dhaka tribune, all the dhaka news and national news are marked as "national", other wise tried to find the location whule crawling using thier tag. Still we have to find and verifiy the locations using NER tagging)
- is_negative : `boolean`

A python list of districts:

```
districts = ["Barisal","Bagerhat","Bandarban","Barguna","Bhola","Brahmanbaria","Bogra","Chandpur","Chittagong","Chuadanga","Comilla","Coxs Bazar","Dhaka","Dinajpur","Feni","Faridpur","Gaibandha","Gazipur","Gopalganj","Habiganj","Jessore","Jhalakati","Jamalpur","Joypurhat","Jhenaidah","Kurigram","Khulna","Khagrachari","Kustia","Kishorganj","Laxmipur","Lalmonirhat","Madaripur","Magura","Meherpur","Moulvibazar","Mymensingh","Manikgonj","Munsiganj","Narail","Narayangonj","Noakhali","Naogaon","Narsingdi","Natore","Nawabgonj","Netrokona","Nilphamari","Pabna","Panchagarh","Patuakhali","Pirojpur","Rajshahi","Rajbari","Rangamati","Rangpur","Sylhet","Shariatpur","Satkhira","Sherpur","Sirajganj","Sunamgonj","Tangail","Thakurgaon"]
```
