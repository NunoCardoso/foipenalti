# -*- coding: utf-8 -*-

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

class DetalheCompeticaoSumario(DetalheCompeticao):
		
	cache_namespace = "detalhe_competicao_sumario"

	acu_class_real = None
	acu_class_virtual = None

	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		return self.requestHandler()
	
	# este verifica acumulador, não o cmp_ultima_alteracao
	# por isso, esta funcção tem que fazer um override.
	def checkCacheFreshen(self):
		
		data_cache = None # data do HTML gerado em cache
		
		self.softcache_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_html:
			data_cache = self.softcache_html['date']
		else:
			self.hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if self.hardcache_html:
				data_cache = self.hardcache_html.cch_date
	
		self.acu_class_real = memcache.get("acumulador-%s-%s" % (self.competicao, config.VERSAO_ACUMULADOR), namespace="classificacao_real")
		if not self.acu_class_real:
			self.acu_class_real = classes.getAcumuladorCompeticao(
				self.competicao,  config.VERSAO_ACUMULADOR,"classificacao_real")
		if data_cache and self.acu_class_real and self.acu_class_real.acuc_date > data_cache:
			self.refreshen_cache = True
		
		self.acu_class_virtual = memcache.get("acumulador-%s-%s" % (self.competicao, config.VERSAO_ACUMULADOR), namespace="classificacao_virtual")
		if not self.acu_class_real:
			self.acu_class_real = classes.getAcumuladorCompeticao(
				self.competicao,  config.VERSAO_ACUMULADOR,"classificacao_virtual")
		if data_cache and self.acu_class_virtual and self.acu_class_virtual.acuc_date > data_cache:
			self.refreshen_cache = True
					
	def renderDados(self):
		
		# classificacao
		classificacao_real = None
		if self.acu_class_real:
			classificacao_real = self.acu_class_real.acuc_content["classificacao_real"]
		else:
			acuc = classes.getAcumuladorCompeticao(
				self.competicao, config.VERSAO_ACUMULADOR,"classificacao_real")
			if acuc:
			   classificacao_real = acuc.acuc_content["classificacao_real"]
			
		classificacao_virtual = None			
		if self.acu_class_virtual:
			classificacao_virtual = self.acu_class_virtual.acuc_content["classificacao_virtual"]
		else:
			acuc = classes.getAcumuladorCompeticao(
				self.competicao, config.VERSAO_ACUMULADOR,"classificacao_virtual")
			if acuc:
				classificacao_virtual = acuc.acuc_content["classificacao_virtual"]
		
		clubes = {}
		
		if classificacao_real and classificacao_real.has_key("total"):
			for idx, item in enumerate(classificacao_real["total"]):
				# fill out clubes.
				c = Clube.get_by_id(classificacao_real["total"][idx]["clu"])
				classificacao_real["total"][idx]["clube"] = c
				clubes[c.key().id()] = {"id":c.key().id(), "nome":c.clu_nome_curto, "logo":c.clu_link_logo} 
		
		if classificacao_virtual and classificacao_virtual.has_key("total"):
			for idx, item in enumerate(classificacao_virtual["total"]):
				classificacao_virtual["total"][idx]["clube"] = Clube.get_by_id(classificacao_virtual["total"][idx]["clu"])
		
		# tenho de enviar uma lista de clubes e a sua info, para que o javascript de desenho 
		# da classificação possa fazer nas classificações parciais. Não é inteligente adicionar 
		# objectos clubes em cada versão de classificação parcial

		# top jogadores
		melhores_marcadores = []
		mais_indisciplinados = []
		top_jogadores = None
					
		top_list_melhores_marcadores = 5
		top_list_mais_indisciplinados = 5
		
		# top jogadores: 
		acuc = classes.getAcumuladorCompeticao(self.competicao, 
			config.VERSAO_ACUMULADOR, "top_jogadores")
		if acuc:
			top_jogadores = acuc.acuc_content["top_jogadores"]
		
		if top_jogadores:
			howmany = len(top_jogadores["mais_golos"]) if len(top_jogadores["mais_golos"]) <= top_list_melhores_marcadores else top_list_melhores_marcadores
			for linha in top_jogadores["mais_golos"][:howmany]:
				melhores_marcadores.append(linha)

			howmany = len(top_jogadores["mais_cartoes"]) if len(top_jogadores["mais_cartoes"]) <= top_list_mais_indisciplinados else top_list_mais_indisciplinados
			for linha in top_jogadores["mais_cartoes"][:howmany]:
				mais_indisciplinados.append(linha)

			# vamos recolher os ids de todos os jogadores
			ids = []
			for item in melhores_marcadores:
				# item = {jgd:1L, gol:1L}
				if not item["jgd"] in ids:
					ids.append(item["jgd"])
			for item in mais_indisciplinados:
				# item = {jgd:1L, crt:{ca:, cda: cv: tot:}}
				if not item["jgd"] in ids:
					ids.append(item["jgd"])
		
			# agora vamos obter os objectos, e fazer uma hash invertida.
			jogadores = Jogador.get_by_id(ids)
			jgds = {}
			for jogador in jogadores: 
				jgds[jogador.key().id()] = jogador
		
			# agora vamos substituir os ids pelos objectos
			for idx, val in enumerate(melhores_marcadores):
				melhores_marcadores[idx]["jogador"] = jgds[val["jgd"]]
			for idx, val in enumerate(mais_indisciplinados):
				mais_indisciplinados[idx]["jogador"] = jgds[val["jgd"]]
		
		dados = {
			"melhores_marcadores":melhores_marcadores,
			"mais_indisciplinados":mais_indisciplinados,
			"clubes":clubes
		}
		
		if classificacao_real and classificacao_real.has_key("total"):
			dados["classificacao_real"] = classificacao_real["total"] 
			
		if classificacao_real and classificacao_real.has_key("parcial"):
			dados["classificacao_real_parcial"] = classificacao_real["parcial"] 
		
		if classificacao_virtual and classificacao_virtual.has_key("total"):
			dados["classificacao_virtual"] = classificacao_virtual["total"]

		if classificacao_virtual and classificacao_virtual.has_key("parcial"):
			dados["classificacao_virtual_parcial"] = classificacao_virtual["parcial"] 

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('competicao','detalhe_competicao_sumario.html', {
			"classificacao_real": self.dados['classificacao_real'] if  self.dados.has_key('classificacao_real') else None,
			"classificacao_virtual": self.dados['classificacao_virtual'] if self.dados.has_key('classificacao_virtual') else None, 
			"classificacao_real_parcial": self.dados['classificacao_real_parcial'] if  self.dados.has_key('classificacao_real_parcial') else None,
			"classificacao_virtual_parcial": self.dados['classificacao_virtual_parcial'] if self.dados.has_key('classificacao_virtual_parcial') else None, 
			"melhores_marcadores":self.dados["melhores_marcadores"],
			"mais_indisciplinados":self.dados["mais_indisciplinados"],
			"clubes":self.dados["clubes"],
			"competicao": self.competicao,
			"data":datetime.datetime.now()
		})
		return html