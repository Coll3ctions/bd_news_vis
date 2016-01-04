bd_news_vis collaboration

### Todo list
- daily star crawled text (salman)
- dhaka tribune crawled text (mishuk)
- prothom alo english version crawled text (mishuk?)
- NER tagging (khalid, script done)
- d3plus visualization (saquib)
- server space (saquib, done)

### Issues (add more to keep track)
- ~~xpath parsing not returning 0 or null results (mishuk)~~
- scrapy crawling not working with xpath (salman)
- d3plus map not showing full region (saquib)

### Data analysis methods (ideas)
- PCA on entity-location matrix (locations are columns/dimensions)
- DTW (dynamic time warping) on time series of popularity/attention of entities.
- Devise a metric for popularity decay that takes account of
  - width of waves (w_1, ..., w_n)
  - period between waves (T_1, ..., T_(n-1))
  - amplitude and/or area under the curve of a particular pulse (A_1, ..., A_n)
  - Reward function for frequent show-ups of entities.
  - We may need to sub-sample the time series to make the above quantities meaningful.
- Come up with a metric for comparing newspapers (giving a formal structure to previous newspaper area coverage work)
  - This metric can take account of mutual information overlap between two newspapers based on an ensemble of entities and their relative coverage.
  - entity in this case may mean location or person.

### Further ideas:
- decay rate of public memory (characteristic rate for every country?)
- does climate change correlate with news trend?
- policy making data available? any correlation with public memory decay rate?
- network analysis between entities
- Fulfillment of promises by polittical leaders (maybe far fetched but still worth exploring)

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
