# -*- coding: utf-8 -*-
from google.appengine.api import memcache
import logging
import urlparse
import time
import re
import os
import datetime
import sys

from urlparse import *

# lista de memcaches para confirmar datas
def check(cacheresultados, lista):
	
	cache_old = False
	for elem in lista:
		cache = memcache.get(elem)
		if cache and cache['date'] > cacheresultados['date']:
			cache_old = True
	
	return cache_old	 
