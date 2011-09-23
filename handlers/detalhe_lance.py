# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from google.appengine.api import memcache
from lib.mycachehandler import MyCacheHandler

class DetalheLance(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_lance"
	cache_url = None

	#memcache values
	dados = None
	html = None
	sid = None

	# get vars
	lance = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.lance:
			error = u"Erro: Não há lance com os parâmetros dados."
			logging.error(error)
			new_sid = self.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)	
			return
		
		self.checkCacheFreshen()
		self.requestHandler()
		self.lance.lan_numero_visitas += 1
		self.lance.put() 
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
		
		if data_cache and self.lance.lan_ultima_alteracao > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		
		lances_siblings = self.lance.lan_jogo.jog_lances
		lance_anterior = None
		lance_posterior = None
		for lan in lances_siblings:
			if lan.lan_numero == self.lance.lan_numero - 1:
				lance_anterior = lan
			if lan.lan_numero == self.lance.lan_numero + 1:
				lance_posterior = lan
				
		dados = {
			"lance": self.lance, 
			"lance_anterior":lance_anterior,
			"lance_posterior":lance_posterior,
			"comentarios":self.lance.lan_comentadores.fetch(1000),
			"protagonistas": self.lance.lan_jogadores.fetch(1000),
			"tipo": Lance.translation_classe[self.lance.lan_classe]
		}	
		return dados

	def renderHTML(self):
		flash_message = None
		if self.sid:
			flash_message = memcache.get(str(self.sid), namespace="flash")
			if flash_message:
				memcache.delete(str(self.sid), namespace="flash")
		
		html = self.render('detalhe_lance.html', {
			"lance_html":self.render_subdir("gera","gera_lance.html", {
				"lance":self.dados
			}),
			"lance_anterior":self.dados['lance_anterior'],
			"lance_posterior":self.dados['lance_posterior'],
			"lance":self.dados['lance'],
			"flash":flash_message
		})
		return html
		
	def decontaminate_vars(self):
		
		lan_id = None
		lance = None

		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_lance"

		self.sid =self.get_sid_from_cookie()
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		try:
			lan_id = int(self.request.get("id"))
			lance = Lance.get_by_id(lan_id) 
		except:
			pass
				
		if lance:
			self.lance = lance
			self.cache_url = self.request.path+"?id="+str(lance.key().id())