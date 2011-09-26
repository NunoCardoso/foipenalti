# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes
from classes import *
from lib import calendario
from detalhe_arbitro import DetalheArbitro

class DetalheArbitroJogos(DetalheArbitro):
		
	# memcache vars
	cache_namespace = "detalhe_arbitro_jogos"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 
		
	def renderDados(self):
		
		dados = {
			"calendario_epoca":None,
			"jogos_calendario":None,
			"jogos":[]
		}
				
		# self.epoca dá-me a época pela qual quero filtrar os jogos
		dados["jogos"] = self.arbitro.arb_jogos.filter("jog_epoca = ", self.epoca).order("-jog_data").fetch(1000)
	
		calendario_epoca, jogos_calendario =  calendario.gera_calendario_epoca(self.epoca, dados["jogos"])	
		dados["calendario_epoca"] = calendario_epoca
		dados["jogos_calendario"] = jogos_calendario

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('arbitro','detalhe_arbitro_jogos.html', {
			"jogos":self.dados["jogos"],
			"arbitro":self.arbitro,
			"epoca":self.epoca,
			"data":datetime.datetime.now(),
			"calendario_epoca":self.dados["calendario_epoca"],
			"jogos_calendario":self.dados["jogos_calendario"]
		})
	
		return html
	