# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_competicao import DetalheCompeticao
from lib import calendario

class DetalheCompeticaoJogos(DetalheCompeticao):
		
	# memcache vars
	cache_namespace = "detalhe_competicao_jogos"
	render_this_page_without_main = True

	# objecto do respectivo acumulador
	nspace = "top_jogos"
	acuc_obj = None
	
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
	
		self.acuc_obj = memcache.get("acumulador-%s-%s" % (self.competicao, config.VERSAO_ACUMULADOR),
		 namespace=self.nspace)
		if not self.acuc_obj:
			self.acuc_obj = classes.getAcumuladorCompeticao(self.competicao, config.VERSAO_ACUMULADOR, self.nspace)
		
		if data_cache and self.acuc_obj and self.acuc_obj.acuc_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):

		acumulador = None
		dados = {}
		
		limit_mais_golos = 10
		limit_maiores_goleadas = 10
		limit_mais_indisciplina = 10
		limit_mais_icc = 10
		
		if self.acuc_obj:
			acumulador = self.acuc_obj.acuc_content[self.nspace]
		else:
			acumulador = classes.getAcumuladorCompeticao(self.competicao, config.VERSAO_ACUMULADOR, self.nspace).acuc_content[self.nspace]

		dados["jogos"] = self.competicao.cmp_jogos.order("-jog_data").fetch(1000)
		
		# aproveito e gero uma hash invertida
		jogs = {}
		for jogo in dados["jogos"]: 
			jogs[jogo.key().id()] = jogo
		
		# no HTML, escrever só as entradas que tem clube. 
		# se não tiver, são de clubes acessórios e não importantes
		for key, list_values in acumulador.items():
			for idx, val in enumerate(acumulador[key]):
				acumulador[key][idx]["jogo"] = jogs[acumulador[key][idx]["jog"]]
					 		
		calendario_competicao, jogos_calendario =  calendario.gera_calendario_epoca(self.competicao.cmp_epoca, dados["jogos"])	

		dados["calendario_competicao"] = calendario_competicao
		dados["jogos_calendario"] = jogos_calendario
			
		howmany = len(acumulador["mais_golos"]) if len(acumulador["mais_golos"]) <= limit_mais_golos else limit_mais_golos
		dados["mais_golos"] = acumulador["mais_golos"][:howmany]
		howmany = len(acumulador["maiores_goleadas"]) if len(acumulador["maiores_goleadas"]) <= limit_maiores_goleadas else limit_maiores_goleadas
		dados["maiores_goleadas"] = acumulador["maiores_goleadas"][:howmany]
		howmany = len(acumulador["mais_indisciplina"]) if len(acumulador["mais_indisciplina"]) <= limit_mais_indisciplina else limit_mais_indisciplina
		dados["mais_indisciplina"] = acumulador["mais_indisciplina"][:howmany]
		howmany = len(acumulador["mais_icc"]) if len(acumulador["mais_icc"]) <= limit_mais_icc else limit_mais_icc
		dados["mais_icc"] = acumulador["mais_icc"][:howmany]
	
		# jornadas
		dados["jornadas"] = self.competicao.cmp_jornadas.order("jor_ordem").fetch(1000)

		return dados

	def renderHTML(self):

		jornadas_html = []
		jornadas_html3 = []
		counter = 0
		for jornada in self.dados["jornadas"]:
			# vamos fazer batches de 3
			counter += 1
			
			jornadas_html3.append(self.render_subdir("gera",'gera_tabela_jornada.html', {
				"jornada": jornada,
				"competicao": self.competicao
			}))
			if counter % 3 == 0:
				jornadas_html.append(jornadas_html3)
				jornadas_html3 = []
		
		# leftover
		if jornadas_html3 != []:
			jornadas_html.append(jornadas_html3)

		html = self.render_subdir('competicao','detalhe_competicao_jogos.html', {
			"jornadas_html": jornadas_html,
			"jogos":self.dados["jogos"],
			"calendario_competicao":self.dados["calendario_competicao"],
			"jogos_calendario":self.dados["jogos_calendario"],
		
			"mais_golos":self.dados["mais_golos"],
			"maiores_goleadas":self.dados["maiores_goleadas"],
			"mais_icc":self.dados["mais_icc"],
			"mais_indisciplina":self.dados["mais_indisciplina"],

			"competicao": self.competicao,
			"data":datetime.datetime.now()
		})
		return html
