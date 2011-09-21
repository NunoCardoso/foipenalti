# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 

from classes import *
from lib import mymemcache 
from lib.myhandler import MyHandler

class LerPaginaJogo(MyHandler):
	
	def get(self):

		