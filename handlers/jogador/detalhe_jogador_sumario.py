# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_jogador import DetalheJogador

class DetalheJogadorSumario(DetalheJogador):
		
	# memcache vars
	cache_namespace = "detalhe_jogador_sumario"
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		dados = []

		# pode haver mais que um, por cada competicao
		acumuladores = AcumuladorCompeticao.all().filter("acuc_epoca = ", self.epoca).filter("acuc_versao = ", config.VERSAO_ACUMULADOR).filter("acuc_namespace = ", "jogador")
		for acu in acumuladores:
						
			if acu.acuc_content["jogador"].has_key(self.jogador.key().id()):
				top_jogador = acu.acuc_content["jogador"][self.jogador.key().id()]
			
				for clube_key, clube_values in top_jogador.items():
		
					dados.append({
					"epoca":acu.acuc_epoca,
					"competicao":acu.acuc_competicao,
					"clube":Clube.get_by_id(clube_key),
					"jogos_realizados":clube_values["jr"],
					"minutos_jogados":clube_values["mj"],
					"golos_marcados":clube_values["gm"],
					"cartoes_amarelos":clube_values["ca"],
					"cartoes_duplo_amarelos":clube_values["cda"],
					"cartoes_vermelhos":clube_values["cv"],
					"indisciplina":clube_values["ca"]+\
						1.5*clube_values["cda"]+\
						2*clube_values["cv"]
				})

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('jogador','detalhe_jogador_sumario.html', {
			"dados":self.dados,
			"jogador":self.jogador,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html
	