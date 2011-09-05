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

class DetalheClube(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_clube"
	cache_url = None

	#memcache values
	dados = None
	html = None
	sid = None
	
	# get vars
	epoca = None
	clube = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.clube:
			error = u"Erro: Não há clube com os parâmetros dados."
			logging.error(error)
			new_sid = mymemcache.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.redirect(mymemcache.add_sid_to_url(self.referer, new_sid))
			return

		self.checkCacheFreshen()
		self.requestHandler()
		self.clube.clu_numero_visitas += 1
		self.clube.put() 
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
		
		if data_cache and self.clube.clu_ultima_alteracao > data_cache:
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
		
		html = self.render_subdir('clube','detalhe_clube.html', {
			"clube": self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now(),
			"flash":flash_message
		})
		return html
		
	def decontaminate_vars(self):
		
		clube = None

		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_clube"
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		self.sid = self.request.get("sid")

		# clube pode ser passado com parâmetro clube, id ou q
		if self.request.get("clube"):
			clube = Clube.all().filter("clu_nome =",self.request.get("clube")).get()

		if not clube:
			clube = Clube.all().filter("clu_nome_curto =",self.request.get("clube")).get()
		
		if not clube:
			if self.request.get("id"):
				try: 
					clube = Clube.get_by_id(int(self.request.get("id")))
				except:
					pass
		
		if clube:
			self.clube = clube
		
			# 1. predefinir variaveis: epoca e competicao
			if self.request.get("epoca"): # formato epo_nome:cmp_tipo
				self.epoca = Epoca.all().filter("epo_nome = ",  self.request.get("epoca")).get()
		
			if not self.epoca:
				self.epoca = config.EPOCA_CORRENTE
		
			# request.path starts with "/"
			self.cache_url = self.request.path+"?id="+str(clube.key().id())+"&epoca="+self.epoca.__str__()
