# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
d = datetime.datetime(2011, 10, 12)
cac = CacheHTML.all().filter("cch_date < ", d).order("-cch_date").fetch(1000)
count = 0
for c in cac:
	if c.cch_content is not None:
		c.cch_content = None
		c.put()
		count = count + 1
		print str(count) + ": "+ str(c.cch_date)