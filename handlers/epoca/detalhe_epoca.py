# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from lib import mymemcache
from google.appengine.api import memcache
from lib.mycachehandler import MyCacheHandler

class DetalheEpoca(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_epoca"
	cache_url = None

	#memcache values
	dados = None
	html = None
	sid = None

	# get vars
	epoca = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.epoca: 	
			error = u"Erro: Não há época com os parâmetros dados."
			logging.error(error)
			new_sid = mymemcache.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.redirect(mymemcache.add_sid_to_cookie(self.referer, new_sid))
			return

		self.checkCacheFreshen()
		self.requestHandler()
		self.epoca.epo_numero_visitas += 1
		self.epoca.put() 
		return 
		
	# este verifica cmp_ultima_aleracao, não o acumulador
	def checkCacheFreshen(self):
		
		data_cache = None # data do HTML gerado em cache
		
		self.softcache_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_html:
			data_cache = self.softcache_html['date']
		else:
			self.hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if self.hardcache_html:
				data_cache = self.hardcache_html.cch_date
		
		if data_cache and self.epoca.epo_ultima_alteracao > data_cache:
			self.refreshen_cache = True

	# não há nada para devolver	
	def renderDados(self):
		return {}

	def renderHTML(self):
		flash_message = None
		if self.sid:
			flash_message = memcache.get(str(self.sid), namespace="flash")
			if flash_message:
				memcache.delete(str(self.sid), namespace="flash")
		
		html = self.render_subdir('epoca','detalhe_epoca.html', {
			"epoca": self.epoca,
			"data":datetime.datetime.now(),
			"flash":flash_message
		})
		return html
		
	def decontaminate_vars(self):
		
		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_epoca"

		self.sid = get_sid_from_cookie()
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		if self.request.get("id"): # formato epo_nome:cmp_tipo
			self.epoca = Epoca.get_by_id(int(self.request.get("id")))

		if not self.epoca:
			if self.request.get("epoca"): # formato epo_nome:cmp_tipo
				self.epoca = Epoca.all().filter("epo_nome = ", self.request.get("epoca")).get()
		
		if not self.epoca:
			self.epoca = config.EPOCA_CORRENTE
		
		# request.path starts with "/"
		self.cache_url = self.request.path+"?id="+str(self.epoca.key().id())
