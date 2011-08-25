# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_competicao import DetalheCompeticao
from google.appengine.api import memcache

class DetalheCompeticaoArbitros(DetalheCompeticao):
		
	# memcache vars
	cache_namespace = "detalhe_competicao_arbitros"

	# objecto do respectivo acumulador
	nspace = "top_arbitros"
	acuc_obj = None
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		return self.requestHandler()
		
	# este verifica acumulador, não o cmp_ultima_alteracao
	def checkCacheFreshen(self):
		
		data_cache = None # data do HTML gerado em cache
		
		self.softcache_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_html:
			data_cache = self.softcache_html['date']
		else:
			self.hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if self.hardcache_html:
				data_cache = self.hardcache_html.cch_date
	
		self.acuc_obj = memcache.get("acumulador-%s-%s" % ( self.competicao, config.VERSAO_ACUMULADOR),
		 namespace=self.nspace)
		if not self.acuc_obj:
			self.acuc_obj = classes.getAcumuladorCompeticao(self.competicao, config.VERSAO_ACUMULADOR, self.nspace)
		
		if data_cache and self.acuc_obj and self.acuc_obj.acuc_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		acumulador = None
		if self.acuc_obj:
			acumulador = self.acuc_obj.acuc_content[self.nspace]
		else:
			acumulador = classes.getAcumuladorCompeticao(self.competicao, config.VERSAO_ACUMULADOR, self.nspace).acuc_content[self.nspace]
		
		arb_ids = []
		hash_arbitros = {}
		
		for key, list_values in acumulador.items():
			for idx, val in enumerate(acumulador[key]):
				if not acumulador[key][idx]["arb"] in arb_ids:
					arb_ids.append(acumulador[key][idx]["arb"])
	
		# converter ids em Arbitros
		arb_objs = Arbitro.get_by_id(arb_ids)
		for arb in arb_objs:
			hash_arbitros[arb.key().id()] = arb
			
		for key, list_values in acumulador.items():
			for idx, val in enumerate(acumulador[key]):
				acumulador[key][idx]["arbitro"] = hash_arbitros[acumulador[key][idx]["arb"]]

		return acumulador


	def renderHTML(self):
		#logging.info("renderHTML")
		html = self.render_subdir('competicao','detalhe_competicao_arbitros.html', {
			"competicao":self.competicao,
			"cartoes_mostrados":self.dados["cartoes_mostrados"],
			"mais_icc":self.dados["mais_icc"],
			"data":datetime.datetime.now()
		})

		return html
