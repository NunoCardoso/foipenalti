# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from google.appengine.api import memcache
from lib.mycachehandler import MyCacheHandler

class DetalheArbitro(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_arbitro"
	cache_url = None
	
	render_this_page_without_main = False
	
	#memcache values
	dados = None
	html = None
	title = None
	
	sid = None

	# get vars
	epoca = None
	arbitro = None
	
	referer = None
		
	def get(self):
		self.decontaminate_vars()
		if not self.arbitro:
			error = u"Erro: Não encontrei árbitro com os parâmetros dados. Use a pesquisa para o encontrar, por favor."
			logging.error(error)
			new_sid = self.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(self.referer)	
			return
		self.checkCacheFreshen()
		self.checkIfAdminUser()
		self.requestHandler()
		self.arbitro.arb_numero_visitas += 1
		self.arbitro.put() 
		return 
		
	def checkCacheFreshen(self):
		data_cache = None # data do HRML gerado em cache
		
		self.softcache_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_html:
			data_cache = self.softcache_html['date']
		else:
			self.hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if self.hardcache_html:
				data_cache = self.hardcache_html.cch_date
		
		if data_cache and self.arbitro.arb_ultima_alteracao > data_cache:
			self.refreshen_cache = True
		
	def renderDados(self):
		return {
			"epoca":self.epoca
		}

	def renderHTML(self):
		
		flash_message = None
		if self.sid:
			flash_message = memcache.get(str(self.sid), namespace="flash")
			if flash_message:
				memcache.delete(str(self.sid), namespace="flash")

		html = self.render_subdir('arbitro','detalhe_arbitro.html', {
			"arbitro": self.arbitro,
			"epoca":self.epoca,
			"data":datetime.datetime.now(),
			"flash":flash_message
		})
		return html
	
	def renderTitle(self):
		return self.arbitro.arb_nome
		
	def decontaminate_vars(self):
		
		arbitro = None

		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_arbitro"
		
		self.sid =self.get_sid_from_cookie()
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		arb_id = self.request.get("id")
		try:
			arbitro = Arbitro.get_by_id(int(arb_id))
		except:
			pass
			
		if not arbitro:
			q = self.request.get("arbitro")
			if q:
				try:
					arbitro = Arbitro.all().filter("arb_nome = ", q).get()
				except:
					pass
			
		if arbitro:
			self.arbitro = arbitro
		
			# 1. predefinir variaveis: epoca e competicao
			if self.request.get("epoca"): # formato epo_nome:cmp_tipo
				self.epoca = Epoca.all().filter("epo_nome = ",  self.request.get("epoca")).get()
		
			if not self.epoca:
				self.epoca = config.EPOCA_CORRENTE
		
			# request.path starts with "/"
			self.cache_url = self.request.path+"?id="+str(arbitro.key().id())+"&epoca="+self.epoca.__str__()
