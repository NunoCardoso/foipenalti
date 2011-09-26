# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_clube import DetalheClube

class DetalheClubeArbitros(DetalheClube):
		
	# memcache vars
	cache_namespace = "detalhe_clube_arbitros"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		dados = {}
		epoca_corrente = config.EPOCA_CORRENTE		

		acumulador = classes.getAcumuladorEpoca(self.epoca, 
			config.VERSAO_ACUMULADOR, "clube")
		
		if acumulador and acumulador.acue_content["clube"].has_key(self.clube.key().id()):
			top_clube = acumulador.acue_content["clube"][self.clube.key().id()]
		
			arbitros = {}
			arb_ids = []
			hash_arbitros = {}
			
			#logging.info(top_jogadores.keys())
			for arbitro_id, jogos in top_clube["a_j"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
					"jogos_realizados":0,
					"icc":0,
					"cartoes_amarelos":0,
					"cartoes_duplo_amarelos":0,
					"cartoes_vermelhos":0,
					"indisciplina":0
				}
				arbitros[arbitro_id]["jogos_realizados"] += jogos
				arb_ids.append(arbitro_id)

			for arbitro_id, icc  in top_clube["a_i"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
					"jogos_realizados":0,
					"icc":0,
					"cartoes_amarelos":0,
					"cartoes_duplo_amarelos":0,
					"cartoes_vermelhos":0,
					"indisciplina":0
				}
				arbitros[arbitro_id]["icc"] += icc
				arb_ids.append(arbitro_id)
			
			for arbitro_id, amarelo in top_clube["a_a"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
					"jogos_realizados":0,
					"icc":0,
					"cartoes_amarelos":0,
					"cartoes_duplo_amarelos":0,
					"cartoes_vermelhos":0,
					"indisciplina":0
				}
				arbitros[arbitro_id]["cartoes_amarelos"] += amarelo
				arbitros[arbitro_id]["indisciplina"] += amarelo
				arb_ids.append(arbitro_id)
			
			for arbitro_id, damarelo in top_clube["a_da"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
			 		"jogos_realizados":0,
			 		"icc":0,
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
				}
				arbitros[arbitro_id]["cartoes_duplo_amarelos"] += damarelo
				arbitros[arbitro_id]["indisciplina"] += 1.5 * damarelo
				arb_ids.append(arbitro_id)

			for arbitro_id, vermelho in top_clube["a_v"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
			 		"jogos_realizados":0,
			 		"icc":0,
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
				}
				arbitros[arbitro_id]["cartoes_vermelhos"] += vermelho
				arbitros[arbitro_id]["indisciplina"] += 2 * vermelho
				arb_ids.append(arbitro_id)

			# converter ids em Arbitros
			arb_objs = Arbitro.get_by_id(arb_ids)
			for arb in arb_objs:
				hash_arbitros[arb.key().id()] = arb
			
			# adicionar o objecto
			for arb_id, arb_value in arbitros.items():
				arbitros[arb_id]["arbitro"] = hash_arbitros[arb_id]

			dados = arbitros.values()

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('clube','detalhe_clube_arbitros.html', {
			"arbitros":self.dados,
			"clube":self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html
	