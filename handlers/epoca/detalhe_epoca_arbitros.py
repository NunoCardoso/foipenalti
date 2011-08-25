# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_epoca import DetalheEpoca
from google.appengine.api import memcache

class DetalheEpocaArbitros(DetalheEpoca):
		
	# memcache vars
	cache_namespace = "detalhe_epoca_arbitros"

	# objecto do respectivo acumulador
	nspace = "top_arbitros"
	acue_obj = None
	
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
	
		self.acue_obj = memcache.get("acumulador-%s-%s" % ( self.epoca, config.VERSAO_ACUMULADOR),
		 namespace=self.nspace)
		if not self.acue_obj:
			self.acue_obj = classes.getAcumuladorEpoca(self.epoca, config.VERSAO_ACUMULADOR, self.nspace)
		
		if data_cache and self.acue_obj and self.acue_obj.acue_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		acumulador = None
		if self.acue_obj:
			acumulador = self.acue_obj.acue_content[self.nspace]
		else:
			acumulador = classes.getAcumuladorEpoca(self.epoca, config.VERSAO_ACUMULADOR, self.nspace).acue_content[self.nspace]
		
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
		html = self.render_subdir('epoca','detalhe_epoca_arbitros.html', {
			"epoca":self.epoca,
			"cartoes_mostrados":self.dados["cartoes_mostrados"],
			"mais_icc":self.dados["mais_icc"],
			"data":datetime.datetime.now()
		})

		return html
