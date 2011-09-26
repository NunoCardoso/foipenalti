# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from detalhe_jogador import DetalheJogador

class DetalheJogadorJogos(DetalheJogador):
		
	# memcache vars
	cache_namespace = "detalhe_jogador_jogos"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		
		todos_jjj = []
		dados = []		
		date = datetime.datetime.now()
		
		for jjj in self.jogador.jgd_jogos:

			if jjj.jjj_jogo.jog_data and jjj.jjj_jogo.jog_golos_clube1 != None and jjj.jjj_jogo.jog_golos_clube2 != None:
				todos_jjj.append(jjj)
		
		sort = sorted(todos_jjj, cmp=lambda x,y: cmp(x.jjj_jogo.jog_data, y.jjj_jogo.jog_data), reverse=True)
		for jjj in sort:
			
			minutos_jogados = 90
			if jjj.jjj_substituicao_entrada:
				if jjj.jjj_substituicao_entrada >= 90:
					minutos_jogados = jjj.jjj_substituicao_entrada - 90
				else:
					minutos_jogados = 90 - jjj.jjj_substituicao_entrada

			if jjj.jjj_substituicao_saida:
				minutos_jogados = jjj.jjj_substituicao_saida

			dados.append({
				"jogo":jjj.jjj_jogo,
				"minutos_jogados":minutos_jogados,
				"golos":jjj.jjj_golos_minutos,
				"golos_tipos":jjj.jjj_golos_tipos,
				"amarelo":jjj.jjj_amarelo_minuto,
				"duplo_amarelo":jjj.jjj_duplo_amarelo_minuto,
				"vermelho":jjj.jjj_vermelho_minuto
			})
			
		return dados

	def renderHTML(self):
		
		html = self.render_subdir('jogador','detalhe_jogador_jogos.html', {
			"dados":self.dados,
			"jogador":self.jogador,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html
