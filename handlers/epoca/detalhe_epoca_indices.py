# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes
from lib import listas
from classes import *
from detalhe_epoca import DetalheEpoca
from google.appengine.api import memcache

class DetalheEpocaIndices(DetalheEpoca):
		
	# memcache vars
	cache_namespace = "detalhe_epoca_indices"

	# objecto do respectivo acumulador
	nspace1 = "icc"
	nspace2 = "tabela_icc"
	acumulador_icc = None
	acumulador_tabela_icc = None
	
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
	
		self.acumulador_icc = memcache.get("acumulador-%s-%s" % (self.epoca, config.VERSAO_ACUMULADOR),
		 namespace=self.nspace1)
		
		if not self.acumulador_icc:
			self.acumulador_icc = classes.getAcumuladorEpoca(self.epoca, config.VERSAO_ACUMULADOR, self.nspace1)

		if data_cache and self.acumulador_icc and self.acumulador_icc.acue_date > data_cache:
			self.refreshen_cache = True
		
		self.acumulador_tabela_icc = memcache.get("acumulador-%s-%s" % (self.epoca, config.VERSAO_ACUMULADOR),
		 namespace=self.nspace2)
		
		if not self.acumulador_tabela_icc:
			self.acumulador_tabela_icc = classes.getAcumuladorEpoca(self.epoca, config.VERSAO_ACUMULADOR, self.nspace2)

		if data_cache and self.acumulador_tabela_icc and self.acumulador_tabela_icc.acue_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		# já tenho os mesu dois acumuladores, quero é populá-los com clubes e árbitros
		lista_clubes = listas.get_lista_clubes()
		hash_clubes = {}
		lista_arbitros = listas.get_lista_arbitros()
		hash_arbitros = {}

		for clube in lista_clubes:
			hash_clubes[clube.key().id()] = clube
		for arbitro in lista_arbitros:
			hash_arbitros[arbitro.key().id()] = arbitro
	
		# preparar a tabela de icc		
		
		tabela_icc = self.acumulador_tabela_icc.acue_content["tabela_icc"]
		for idx, val in enumerate(tabela_icc):
			if tabela_icc[idx].has_key("arb"):
				tabela_icc[idx]["arbitro"] = hash_arbitros[tabela_icc[idx]["arb"]]
			if tabela_icc[idx].has_key("clus"):
				for idx2, va2 in enumerate(tabela_icc[idx]["clus"]):
					tabela_icc[idx]["clus"][idx2]["clube"] = hash_clubes[tabela_icc[idx]["clus"][idx2]["clu"]]

		# obter a lista de clubes pela qual está ordenada a tabela_icc
		
		clubes = []
		if len(tabela_icc) > 0:
			for idx, val in enumerate(tabela_icc[0]["clus"]):
				logging.info("appending %s" % val["clube"])
				clubes.append(val["clube"])

		# preparar o gráfico de icc
		grafico_icc = self.acumulador_icc.acue_content["icc"]
		for idx, val in enumerate(grafico_icc):
				grafico_icc[idx]["clube"] = hash_clubes[grafico_icc[idx]["clu"]]
		
		dados = {
		"clubes_tabela_icc":clubes,
		"tabela_icc":tabela_icc,
		"grafico_icc":grafico_icc
		}
		return dados

	def renderHTML(self):
		#logging.info("renderHTML")
		html = self.render_subdir('epoca','detalhe_epoca_indices.html', {
			"clubes_tabela_icc":self.dados["clubes_tabela_icc"],
			"tabela_icc":self.dados["tabela_icc"],
			"epoca":self.epoca,
			"grafico":self.render_subdir('gera','gera_grafico_horizontal_icc.html', {
					"icc_dados": self.dados["grafico_icc"],
					"epoca":self.epoca
					
			}),
			"data":datetime.datetime.now()
		})
		return html
