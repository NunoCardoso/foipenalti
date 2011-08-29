# -*- coding: utf-8 -*-
from google.appengine.api import memcache
import logging
import urlparse
import time
import re

from urlparse import *

# lista de memcaches para confirmar datas
def check(cacheresultados, lista):
	
	cache_old = False
	for elem in lista:
		cache = memcache.get(elem)
		if cache and cache['date'] > cacheresultados['date']:
			cache_old = True
	
	return cache_old	 
	
# et milliseconds	
def generate_sid():
	return int(round(time.time() * 1000))

def add_sid_to_url(url, sid):
	
	query = urlparse(url)[4]
	if not query:
		url = url + "?sid="+str(sid)
	else:
		url = re.sub(r'sid=\d+',"", url )
		url = url + "&sid="+str(sid)
	return url
