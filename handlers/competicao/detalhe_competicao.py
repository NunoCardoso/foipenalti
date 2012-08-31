# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from google.appengine.api import memcache
from lib.mycachehandler import MyCacheHandler

class DetalheCompeticao(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_competicao"
	cache_url = None

	render_this_page_without_main = False

	#memcache values
	dados = None
	html = None
	title = None
	
	sid = None
	
	# get vars
	epoca = None
	competicao = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.competicao: 	
			error = u"Erro: Não há competição com os parâmetros dados."
			logging.error(error)
			new_sid = self.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(self.referer)	
			return
		
		self.checkCacheFreshen()
		self.requestHandler()
		self.competicao.cmp_numero_visitas += 1
		self.competicao.put() 
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
		
		if data_cache and self.competicao.cmp_ultima_alteracao > data_cache:
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
        
		html = self.render_subdir('competicao','detalhe_competicao.html', {
			"competicao": self.competicao,
			"epoca":self.epoca,
			"data":datetime.datetime.now(),
			"flash":flash_message
		})
		return html
		
	def renderTitle(self):
		return self.competicao.cmp_nome_completo+" "+self.competicao.cmp_epoca.epo_nome

	def decontaminate_vars(self):
		
		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_competicao"
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		self.sid =self.get_sid_from_cookie()

		if self.request.get("competicao"): 
			q = self.request.get("competicao")
			if q:
				self.competicao = Competicao.all().filter("cmp_nome =", q).get()
				if self.competicao:
					self.epoca = self.competicao.cmp_epoca

		if not self.competicao:
			if self.request.get("id"): 

				try:
					self.competicao = Competicao.get_by_id(int(self.request.get("id")))
					if self.competicao:
						self.epoca = self.competicao.cmp_epoca
				except:
					pass

		# Hack: if we FORCE an epoca, then let's show this competition, on the forced epoca!
		if self.competicao and self.request.get("epoca"): 
			epoca = Epoca.all().filter("epo_nome =", self.request.get("epoca")).get()
			if epoca:
				self.epoca = epoca
				competicao_tipo = self.competicao.cmp_tipo
				self.competicao = Competicao.all().filter("cmp_nome = ", epoca.epo_nome+":"+competicao_tipo).get()

		if not self.competicao:
			self.competicao =  config.COMPETICAO_CORRENTE
			self.epoca = self.competicao.cmp_epoca

		# request.path starts with "/"
		self.cache_url = self.request.path+"?id="+str(self.competicao.key().id())
