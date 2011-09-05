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

class DetalheEpocaClubes(DetalheEpoca):
		
	# memcache vars
	cache_namespace = "detalhe_epoca_clubes"

	# objecto do respectivo acumulador
	nspace = "top_clubes"
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
	
		self.acue_obj = memcache.get("acumulador-%s-%s" % ( self.epoca, config.VERSAO_ACUMULADOR), namespace=self.nspace)
		if not self.acue_obj:
			self.acue_obj = AcumuladorEpoca.all().filter( \
			 "acue_epoca = ", self.epoca).filter("acue_versao = ", config.VERSAO_ACUMULADOR).filter("acue_namespace = ", self.nspace).get()
		
		if data_cache and self.acue_obj and self.acue_obj.acue_date > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		acumulador = None
		if self.acue_obj:
			acumulador = self.acue_obj.acue_content[self.nspace]
		else:
			acumulador =  classes.getAcumuladorEpoca( 
			 self.epoca, config.VERSAO_ACUMULADOR, self.nspace).acue_content[self.nspace]
		
		# agora vamos obter os objectos (clubes) que fazem parte da LIGA desta época
		#, e fazer uma hash invertida.
		liga = self.epoca.epo_competicoes.filter("cmp_tipo = ","Liga").get()

		ac = classes.getAcumuladorCompeticao(liga, config.VERSAO_ACUMULADOR, "clube")
		clus = {}		
		
		if ac:
			clubes_liga_ids = ac.acuc_content["clube"].keys()
		
			clubes = Clube.get_by_id(clubes_liga_ids)

			for clube in clubes: 
				clus[clube.key().id()] = clube
		
		# no HTML, escrever só as entradas que tem clube. 
		# se não tiver, são de clubes acessórios e não importantes
		if acumulador:
			for key, list_values in acumulador.items():
				for idx, val in enumerate(acumulador[key]):
					if clus.has_key(acumulador[key][idx]["clu"]):
						acumulador[key][idx]["clube"] = clus[acumulador[key][idx]["clu"]]
					
		return acumulador

	def renderHTML(self):
		#logging.info("renderHTML")
		html = self.render_subdir('epoca','detalhe_epoca_clubes.html', {
			"epoca":self.epoca,
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