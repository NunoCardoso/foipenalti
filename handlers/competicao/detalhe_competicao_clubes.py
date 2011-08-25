# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes
from lib  import listas

from classes import *
from google.appengine.api import memcache
from detalhe_competicao import DetalheCompeticao

class DetalheCompeticaoClubes(DetalheCompeticao):
		
	# memcache vars
	cache_namespace = "detalhe_competicao_clubes"

	# objecto do respectivo acumulador
	nspace = "top_clubes"
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
	
		self.acuc_obj = memcache.get("acumulador-%s-%s" % (self.competicao,config.VERSAO_ACUMULADOR), namespace=self.nspace)
		if not self.acuc_obj:
			self.acuc_obj = classes.getAcumuladorCompeticao( 
			 self.competicao, config.VERSAO_ACUMULADOR, self.nspace)
		
		if data_cache and self.acuc_obj and self.acuc_obj.acuc_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		acumulador = None
		if self.acuc_obj:
			acumulador = self.acuc_obj.acuc_content[self.nspace]
		else:
			acumulador = classes.getAcumuladorCompeticao( 
			 self.competicao, config.VERSAO_ACUMULADOR, self.nspace)

		clubes = listas.get_lista_clubes()
		clus = {}
		for clube in clubes: 
			clus[clube.key().id()] = clube
		
		# no HTML, escrever só as entradas que tem clube. 
		# se não tiver, são de clubes acessórios e não importantes
		for key, list_values in acumulador.items():
			for idx, val in enumerate(acumulador[key]):
				if clus.has_key(acumulador[key][idx]["clu"]):
					acumulador[key][idx]["clube"] = clus[acumulador[key][idx]["clu"]]

		return acumulador

	def renderHTML(self):
		#logging.info("renderHTML")
		html = self.render_subdir('competicao','detalhe_competicao_clubes.html', {
			"competicao":self.competicao,
			"mais_golos_marcados_e_validados_com_erro_arbitro":self.dados["mais_golos_marcados_e_validados_com_erro_arbitro"],
			"mais_golos_sofridos_e_validados_com_erro_arbitro":self.dados["mais_golos_sofridos_e_validados_com_erro_arbitro"],
			"mais_golos_marcados_e_invalidados_com_erro_arbitro":self.dados["mais_golos_marcados_e_invalidados_com_erro_arbitro"],
			"mais_golos_sofridos_e_invalidados_com_erro_arbitro":self.dados["mais_golos_sofridos_e_invalidados_com_erro_arbitro"],
			"saldo_golos":self.dados["saldo_golos"], 
			"mais_pontos_ganhos_com_erro_arbitro":self.dados["mais_pontos_ganhos_com_erro_arbitro"],
			"mais_pontos_perdidos_com_erro_arbitro":self.dados["mais_pontos_perdidos_com_erro_arbitro"],
			"saldo_pontos":self.dados["saldo_pontos"],
			"mais_icc":self.dados["mais_icc"],
			"mais_indisciplinados":self.dados["mais_indisciplinados"],
			"data":datetime.datetime.now()
		})

		return html