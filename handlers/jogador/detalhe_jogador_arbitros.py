# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_jogador import DetalheJogador

class DetalheJogadorArbitros(DetalheJogador):
		
	# memcache vars
	cache_namespace = "detalhe_jogador_arbitros"

	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		dados = {}
		epoca_corrente = config.EPOCA_CORRENTE		

		acumulador = classes.getAcumuladorEpoca(self.epoca, config.VERSAO_ACUMULADOR, "jogador")
		logging.info(acumulador)
		top_jogador = acumulador.acue_content["jogador"][self.jogador.key().id()]
		
		arbitros = {}
		
		for jogador_key, jogador_values in top_jogador.items():
		
			arbitros = {}
			arb_ids = []
			hash_arbitros = {}
		
			for arbitro_id, amarelo in jogador_values["a_a"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
					}
				arb_ids.append(arbitro_id)
				arbitros[arbitro_id]["cartoes_amarelos"] += amarelo
				arbitros[arbitro_id]["indisciplina"] += amarelo

			for arbitro_id, damarelo in jogador_values["a_da"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
				}
				arb_ids.append(arbitro_id)
				arbitros[arbitro_id]["cartoes_duplo_amarelos"] += damarelo
				arbitros[arbitro_id]["indisciplina"] += 1.5 * damarelo

			for arbitro_id, vermelho in jogador_values["a_v"].items():
				if not arbitros.has_key(arbitro_id):
					arbitros[arbitro_id] = {
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
					}
				arb_ids.append(arbitro_id)
				arbitros[arbitro_id]["cartoes_vermelhos"] += vermelho
				arbitros[arbitro_id]["indisciplina"] += 2 * vermelho

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
		
		html = self.render_subdir('jogador','detalhe_jogador_arbitros.html', {
			"dados":self.dados,
			"jogador":self.jogador,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html
