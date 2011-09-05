# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler

class Admin(MyHandler):
	
	def get(self):
		
		jornada = Jornada.all().order('-jor_ultima_alteracao').get()
		sid = self.request.get('sid')
		flash_message = None
		
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(str(sid), namespace="flash")
					
		self.render_subdir_to_output("admin", 'admin_homepage.html', {
			"jornada":jornada,
			'flash': flash_message
		})
	
