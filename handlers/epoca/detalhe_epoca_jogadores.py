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

class DetalheEpocaJogadores(DetalheEpoca):
		
	# memcache vars
	cache_namespace = "detalhe_epoca_jogadores"

	# objecto do respectivo acumulador
	nspace = "top_jogadores"
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
	
		self.acue_obj = memcache.get("acumulador-%s-%s" % (self.epoca, config.VERSAO_ACUMULADOR),
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
			if jogador:
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
		html = self.render_subdir('epoca','detalhe_epoca_jogadores.html', {
			"epoca":self.epoca,
			"melhores_marcadores":self.dados["mais_golos"],
			"mais_indisciplinados":self.dados["mais_cartoes"],
			"mais_lances":self.dados["mais_lances"],
			"data":datetime.datetime.now()
		})

		return html
