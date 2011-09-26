# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from google.appengine.api import memcache
from detalhe_competicao import DetalheCompeticao

class DetalheCompeticaoJogadores(DetalheCompeticao):
		
	# memcache vars
	cache_namespace = "detalhe_competicao_jogadores"
	render_this_page_without_main = True

	# objecto do respectivo acumulador
	nspace = "top_jogadores"
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
	
		self.acuc_obj = memcache.get("acumulador-%s-%s" % (self.competicao, config.VERSAO_ACUMULADOR),
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

		# vamos recolher os ids de todos os jogadores
		ids = []
		for item in acumulador["mais_golos"]:
			# item = {jgd:1L, gol:1L}
			if not item["jgd"] in ids:
				ids.append(item["jgd"])
		for item in acumulador["mais_cartoes"]:
			# item = {jgd:1L, crt:{ca:, cda: cv: tot:}}
			if not item["jgd"] in ids:
				ids.append(item["jgd"])
		for item in acumulador["mais_lances"]:
			# item = {jgd:1L, crt:{ca:, cda: cv: tot:}}
			if not item["jgd"] in ids:
				ids.append(item["jgd"])
		
		# agora vamos obter os objectos, e fazer uma hash invertida.
		jogadores = Jogador.get_by_id(ids)
		jgds = {}
		for jogador in jogadores: 
			jgds[jogador.key().id()] = jogador
		
		# agora vamos substituir os ids pelos objectos
		for idx, val in enumerate(acumulador["mais_golos"]):
			acumulador["mais_golos"][idx]["jogador"] = jgds[val["jgd"]]
		for idx, val in enumerate(acumulador["mais_cartoes"]):
			acumulador["mais_cartoes"][idx]["jogador"] = jgds[val["jgd"]]
		for idx, val in enumerate(acumulador["mais_lances"]):
			acumulador["mais_lances"][idx]["jogador"] = jgds[val["jgd"]]
	
		return acumulador

	def renderHTML(self):
		#logging.info("renderHTML")
		html = self.render_subdir('competicao','detalhe_competicao_jogadores.html', {
			"competicao":self.competicao,
			"melhores_marcadores":self.dados["mais_golos"],
			"mais_indisciplinados":self.dados["mais_cartoes"],
			"mais_lances":self.dados["mais_lances"],
			"data":datetime.datetime.now()
		})

		return html
