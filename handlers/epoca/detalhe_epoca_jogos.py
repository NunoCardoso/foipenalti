# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_epoca import DetalheEpoca
from lib import calendario

class DetalheEpocaJogos(DetalheEpoca):
		
	# memcache vars
	cache_namespace = "detalhe_epoca_jogos"
	render_this_page_without_main = True

	# objecto do respectivo acumulador
	nspace = "top_jogos"
	acue_obj = None
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

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
	
		self.acue_obj = memcache.get("acumulador-%s-%s" % (self.epoca, config.VERSAO_ACUMULADOR),
		 namespace=self.nspace)
		if not self.acue_obj:
			self.acue_obj = AcumuladorEpoca.all().filter( \
			 "acue_epoca = ", self.epoca).filter("acue_versao = ", config.VERSAO_ACUMULADOR).filter("acue_namespace = ", self.nspace).get()
		
		if data_cache and self.acue_obj and self.acue_obj.acue_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		acumulador = None
		dados = {}
		
		limit_mais_golos = 10
		limit_maiores_goleadas = 10
		limit_mais_indisciplina = 10
		limit_mais_icc = 10
		
		if self.acue_obj:
			acumulador = self.acue_obj.acue_content[self.nspace]
		else:
			acumulador = AcumuladorEpoca.all().filter("acue_epoca = ",self.epoca).filter("acue_versao = ", config.VERSAO_ACUMULADOR).filter("acue_namespace =", self.nspace).get().acue_content[self.nspace]

		dados["jogos"] = self.epoca.epo_jogos.order("-jog_data").fetch(1000)
		
		# aproveito e gero uma hash invertida
		jogs = {}
		for jogo in dados["jogos"]: 
			jogs[jogo.key().id()] = jogo
		
		# no HTML, escrever só as entradas que tem clube. 
		# se não tiver, são de clubes acessórios e não importantes
		for key, list_values in acumulador.items():
			for idx, val in enumerate(acumulador[key]):
				acumulador[key][idx]["jogo"] = jogs[acumulador[key][idx]["jog"]]
					 		
		calendario_epoca, jogos_calendario =  calendario.gera_calendario_epoca(self.epoca, dados["jogos"])	

		dados["calendario_epoca"] = calendario_epoca
		dados["jogos_calendario"] = jogos_calendario
			
		howmany = len(acumulador["mais_golos"]) if len(acumulador["mais_golos"]) <= limit_mais_golos else limit_mais_golos
		dados["mais_golos"] = acumulador["mais_golos"][:howmany]
		howmany = len(acumulador["maiores_goleadas"]) if len(acumulador["maiores_goleadas"]) <= limit_maiores_goleadas else limit_maiores_goleadas
		dados["maiores_goleadas"] = acumulador["maiores_goleadas"][:howmany]
		howmany = len(acumulador["mais_indisciplina"]) if len(acumulador["mais_indisciplina"]) <= limit_mais_indisciplina else limit_mais_indisciplina
		dados["mais_indisciplina"] = acumulador["mais_indisciplina"][:howmany]
		howmany = len(acumulador["mais_icc"]) if len(acumulador["mais_icc"]) <= limit_mais_icc else limit_mais_icc
		dados["mais_icc"] = acumulador["mais_icc"][:howmany]
	
		return dados

	def renderHTML(self):

		html = self.render_subdir('epoca','detalhe_epoca_jogos.html', {
			"jogos":self.dados["jogos"],
			"calendario_epoca":self.dados["calendario_epoca"],
			"jogos_calendario":self.dados["jogos_calendario"],
		
			"mais_golos":self.dados["mais_golos"],
			"maiores_goleadas":self.dados["maiores_goleadas"],
			"mais_icc":self.dados["mais_icc"],
			"mais_indisciplina":self.dados["mais_indisciplina"],

			"epoca": self.epoca,
			"data":datetime.datetime.now()
		})
		return html
