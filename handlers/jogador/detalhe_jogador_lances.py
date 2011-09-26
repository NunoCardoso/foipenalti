# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from detalhe_jogador import DetalheJogador

# devolver por data de jogo. se empatado, por minuto de jogo.
def lance_comparer(jel_lance1, jel_lance2):
    result = cmp(jel_lance1.jel_lance.lan_jogo.jog_data, jel_lance2.jel_lance.lan_jogo.jog_data)
    if result:
      return result
    else:
      return cmp(jel_lance1.jel_lance.lan_minuto, jel_lance2.jel_lance.lan_minuto)

class DetalheJogadorLances(DetalheJogador):
		
	# memcache vars
	cache_namespace = "detalhe_jogador_lances"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		
		todos_jel = []
		dados = []
		date = datetime.datetime.now()
		
		for jel in self.jogador.jgd_lances:
			todos_jel.append(jel)
		
		sort = sorted(todos_jel, cmp=lance_comparer, reverse=True)

		for jel in sort:
			dados.append(jel.jel_lance)
		
		return dados

	def renderHTML(self):
		
		html = self.render_subdir('jogador','detalhe_jogador_lances.html', {
			"lances":self.dados,
			"jogador":self.jogador,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html