# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes
from classes import *
from lib import listas
from detalhe_arbitro import DetalheArbitro

# Nota que herda funções de DetalheArbitro, nomeadamente a 
# decontaminate_values
class DetalheArbitroClubes(DetalheArbitro):
		
	# memcache vars
	cache_namespace = "detalhe_arbitro_clubes"
	render_this_page_without_main = True
	
	# important, to avoid extra count++
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 
		
	def renderDados(self):

		dados = []
		
		acumuladores = AcumuladorCompeticao.all().filter("acuc_epoca = ", self.epoca).filter("acuc_versao = ", config.VERSAO_ACUMULADOR).filter("acuc_namespace = ", "arbitro")
		
		clubes = {}
		
		lista_clubes = listas.get_lista_clubes()
		clus = {}
		for clube in lista_clubes: 
			clus[clube.key().id()] = clube


		for acu in acumuladores:
			if acu.acuc_content["arbitro"].has_key(self.arbitro.key().id()):
				top_arbitro = acu.acuc_content["arbitro"][self.arbitro.key().id()]
		
				for clube_id, jogos in top_arbitro["c_j"].items():
					if not clubes.has_key(clube_id):
						clubes[clube_id] = {
						"clube":clus[clube_id],
			 			"jogos_realizados":0,
			 			"icc":0,
			 			"cartoes_amarelos":0,
			 			"cartoes_duplo_amarelos":0,
			 			"cartoes_vermelhos":0,
			 			"indisciplina":0
					}
					clubes[clube_id]["jogos_realizados"] += jogos
			
				for clube_id, icc  in top_arbitro["c_i"].items():
					if not clubes.has_key(clube_id):
						clubes[clube_id] = {
						"clube":clus[clube_id],
			 			"jogos_realizados":0,
			 			"icc":0,
			 			"cartoes_amarelos":0,
			 			"cartoes_duplo_amarelos":0,
			 			"cartoes_vermelhos":0,
			 			"indisciplina":0
					}
					clubes[clube_id]["icc"] += icc
			
				for clube_id, amarelo in top_arbitro["c_a"].items():
					if not clubes.has_key(clube_id):
						clubes[clube_id] = {
						"clube":clus[clube_id],
			 			"jogos_realizados":0,
			 			"icc":0,
			 			"cartoes_amarelos":0,
			 			"cartoes_duplo_amarelos":0,
			 			"cartoes_vermelhos":0,
			 			"indisciplina":0
					}
					clubes[clube_id]["cartoes_amarelos"] += amarelo
					clubes[clube_id]["indisciplina"] += amarelo

				for clube_id, damarelo in top_arbitro["c_da"].items():
					if not clubes.has_key(clube_id):
						clubes[clube_id] = {
						"clube":clus[clube_id],
			 			"jogos_realizados":0,
			 			"icc":0,
			 			"cartoes_amarelos":0,
			 			"cartoes_duplo_amarelos":0,
			 			"cartoes_vermelhos":0,
			 			"indisciplina":0
					}
					clubes[clube_id]["cartoes_duplo_amarelos"] += damarelo
					clubes[clube_id]["indisciplina"] += 1.5 * damarelo

				for clube_id, vermelho in top_arbitro["c_v"].items():
					if not clubes.has_key(clube_id):
						clubes[clube_id] = {
						"clube":clus[clube_id],
						"jogos_realizados":0,
						"icc":0,
						"cartoes_amarelos":0,
						"cartoes_duplo_amarelos":0,
						"cartoes_vermelhos":0,
						"indisciplina":0
					}
					clubes[clube_id]["cartoes_vermelhos"] += vermelho
					clubes[clube_id]["indisciplina"] += 2 * vermelho

		return clubes.values()
			

	def renderHTML(self):
		
		html = self.render_subdir('arbitro','detalhe_arbitro_clubes.html', {
			"clubes":self.dados,
			"arbitro":self.arbitro,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html