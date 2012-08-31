# -*- coding: utf-8 -*-

from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 
import urllib

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler

from tasks.refresh_acumuladores import *

class AcumuladorTaskManager(MyHandler):
	
	def get(self):
		
		action = self.request.get("action")
		messages = []
		datestring = datetime.datetime.now().strftime("%Y-%m-%d-%Hh%M")

		url = None
		task_name = None
		queue_name="cacherefresh"
		countdown = 0
		
		if action == "refresh1j1c1e":
			
			countdown = int(self.request.get("countdown"))
			versao = self.request.get("versao")
			jornada = self.request.get("jornada")

			task_name = "%s-%s" % (action, datestring)
			url="/task/refresh/1j1c1e?jornada=%s&versao=%s" % (jornada, versao) 
				
		elif action == "refresh1j":
			
			countdown = int(self.request.get("countdown"))
			versao = self.request.get("versao")
			jornada = self.request.get("jornada")

			task_name = "%s-%s" % (action, datestring)
			url="/task/refresh/1j?jornada=%s&versao=%s" % (jornada, versao) 

		elif action == "refresh1e":

			countdown = self.request.get("countdown")
			versao = self.request.get("versao")
			epoca = self.request.get("epoca")

			task_name = "%s-%s" % (action, datestring)
			url="/task/refresh/1e?epoca=%s&versao=%s" % (epoca, versao) 
		
		try:					
			taskqueue.add(
				name = task_name, 
				queue_name="cacherefresh",
				method='GET', 
				#params=task_param, - se o método for post
				url=url, 
				countdown=countdown
			)
		except taskqueue.DuplicateTaskNameError:
			messages.append(u"<span style='color:red'>%s: NOME DUPLICADO.</span>" % url)
		except taskqueue.TaskAlreadyExistsError:
			messages.append(u"<span style='color:red'>%s: TAREFA JÁ EXISTE.</span>" % url)
		except taskqueue.InvalidTaskNameError:
			messages.append(u"<span style='color:red'>%s: NOME da TAREFA INVÁLIDO.</span>" % url)
		except taskqueue.TombstonedTaskError:
			messages.append(u"<span style='color:red'>%s: NOME da TAREFA TEM TOMBA.</span>" % url)
			
		except Exception, e:
			trace = "".join(traceback.format_exc())
			messages.append(u"<span style='color:red'>%s: ERRO %s.</span>" % (url, str(e)))
			messages.append(trace)

		message = u"Tarefa %s adicionada" % task_name
		logging.info(message)
		messages.append(message)
		return "<BR>".join(messages)
