# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from lib.mycachehandler import MyCacheHandler
from google.appengine.api import memcache

class DetalheJogador(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_jogador"
	cache_url = None

	#memcache values
	dados = None
	html = None

	# get vars
	epoca = None
	jogador = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.jogador:
			error = u"Erro: Não há jogador com os parâmetros dados. Use a pesquisa para o encontrar, por favor."
			logging.error(error)
			memcache.set("flash", error)
			self.redirect(self.referer)
			return

		self.checkCacheFreshen()
		self.requestHandler()
		self.jogador.jgd_numero_visitas += 1
		self.jogador.put() 
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
		
		if data_cache and self.jogador.jgd_ultima_alteracao > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		return {
			"epoca":self.epoca
		}

	def renderHTML(self):
		#logging.info("renderHTML")
		
		html = self.render_subdir('jogador','detalhe_jogador.html', {
			"jogador": self.jogador,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
		return html
		
	def decontaminate_vars(self):
		
		jogador = None

		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_jogador"
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		jgd_id = self.request.get("id")
		try: 
			jogador = Jogador.get_by_id(int(jgd_id))
		except:
			pass

		if not jogador:
			q = self.request.get("jogador")
			if q:
				try: 
					jogador = Jogador.all().filter("jgd_nome = ", q).get()
				except:
					pass
			
		if jogador:
			self.jogador = jogador
		
			# 1. predefinir variaveis: epoca e competicao
			if self.request.get("epoca"): # formato epo_nome:cmp_tipo
				self.epoca = Epoca.all().filter("epo_nome = ",  self.request.get("epoca")).get()
		
			if not self.epoca:
				self.epoca = config.EPOCA_CORRENTE
		
			# request.path starts with "/"
			self.cache_url = self.request.path+"?id="+str(jogador.key().id())+"&epoca="+self.epoca.__str__()
