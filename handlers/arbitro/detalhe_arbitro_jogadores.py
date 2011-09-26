# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes
from classes import *
from detalhe_arbitro import DetalheArbitro

# Nota que herda funções de DetalheArbitro, nomeadamente a 
# decontaminate_values
class DetalheArbitroJogadores(DetalheArbitro):
		
	# memcache vars
	cache_namespace = "detalhe_arbitro_jogadores"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 
		
	def renderDados(self):
		dados = {}

		acumulador = classes.getAcumuladorEpoca(self.epoca, config.VERSAO_ACUMULADOR, "arbitro")
						
		top_arbitro = acumulador.acue_content["arbitro"][self.arbitro.key().id()]
		
		ids = []
		jogadores = {}
		
		for jogador_id, amarelo in top_arbitro["j_a"].items():
			if not jogador_id in ids:
			 	ids.append(jogador_id)
				jogadores[jogador_id] = {
					"jgd":jogador_id,
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
				}
				jogadores[jogador_id]["cartoes_amarelos"] += amarelo
				jogadores[jogador_id]["indisciplina"] += amarelo

		for jogador_id, damarelo in top_arbitro["j_da"].items():
				if not jogador_id in ids:
				 	ids.append(jogador_id)
					jogadores[jogador_id] = {
					"jgd":jogador_id,
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
				}
				jogadores[jogador_id]["cartoes_duplo_amarelos"] += damarelo
				jogadores[jogador_id]["indisciplina"] += 1.5 * damarelo

		for jogador_id, vermelho in top_arbitro["j_v"].items():
				if not jogador_id in ids:
				 	ids.append(jogador_id)
					jogadores[jogador_id] = {
					"jgd":jogador_id,
			 		"cartoes_amarelos":0,
			 		"cartoes_duplo_amarelos":0,
			 		"cartoes_vermelhos":0,
			 		"indisciplina":0
				}
				jogadores[jogador_id]["cartoes_vermelhos"] += vermelho
				jogadores[jogador_id]["indisciplina"] += 2 * vermelho


		# agora vamos obter os objectos, e fazer uma hash invertida.
		lista_jogadores = Jogador.get_by_id(ids)
		jgds = {}
		for jogador in lista_jogadores: 
			jgds[jogador.key().id()] = jogador
		
		# agora vamos substituir os ids pelos objectos
		for idx, val in jogadores.items():
			jogadores[idx]["jogador"] = jgds[jogadores[idx]["jgd"]]

		dados = jogadores.values()
		return dados

	def renderHTML(self):
		
		html = self.render_subdir('arbitro','detalhe_arbitro_jogadores.html', {
			"jogadores":self.dados,
			"arbitro":self.arbitro,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html