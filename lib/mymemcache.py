# -*- coding: utf-8 -*-
from google.appengine.api import memcache
import logging
import urlparse
import time
import re
import Cookie
import os
import datetime

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

# add sid to cookie
def add_sid_to_cookie(url, sid):
	expiration = datetime.datetime.now() + datetime.timedelta(minutes=1)
	cookie = Cookie.SimpleCookie()
	cookie["session"]=sid
	cookie["session"]["domain"] = ".foipenalti.com"
	cookie["session"]["path"] = "/sid"
	cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
	 
	#query = urlparse(url)[4]
	#if not query:
	#	url = url + "?sid="+str(sid)
	#else:
	#	url = re.sub(r'sid=\d+',"", url )
	#	url = url + "&sid="+str(sid)
	#	url = re.sub(r'&+',"&", url )
	
	# leave URL untouched
	return url

def get_sid_from_cookie():
	try:
	    cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
	    return cookie["session"].value
	except (Cookie.CookieError, KeyError):
	    logging.info("session cookie sid not set.")