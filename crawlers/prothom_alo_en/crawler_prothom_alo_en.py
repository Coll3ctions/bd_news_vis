import datetime
from dateutil import parser

start_date = parser.parse("2014-07-01")
print start_date
start_date += datetime.timedelta(days=1)
print start_date
#http://www.en.prothom-alo.com/archive/2014-07-01