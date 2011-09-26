# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from google.appengine.api import memcache
from detalhe_arbitro import DetalheArbitro

# Nota que herda funções de DetalheArbitro, nomeadamente a 
# decontaminate_values
class DetalheArbitroLances(DetalheArbitro):
		
	# memcache vars
	cache_namespace = "detalhe_arbitro_lances"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		
		dados = []

		for jogo in self.arbitro.arb_jogos.filter("jog_epoca = ", self.epoca).order("-jog_data"):
			for lance in jogo.jog_lances:
				dados.append(lance)

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('arbitro','detalhe_arbitro_lances.html', {
			"lances":self.dados,
			"arbitro":self.arbitro,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html