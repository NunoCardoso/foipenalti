# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from detalhe_clube import DetalheClube
from lib import calendario

class DetalheClubeJogos(DetalheClube):
		
	# memcache vars
	cache_namespace = "detalhe_clube_jogos"
	
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
		dados["jogos"] = Jogo.all().filter("jog_epoca = ", self.epoca).filter("jog_clubes = ", self.clube.key()).order("jog_data").fetch(1000)
		
		calendario_epoca, jogos_calendario =  calendario.gera_calendario_epoca(self.epoca, dados["jogos"])	
		dados["calendario_epoca"] = calendario_epoca
		dados["jogos_calendario"] = jogos_calendario
		
		return dados

	def renderHTML(self):
		
		html = self.render_subdir('clube','detalhe_clube_jogos.html', {
			"jogo_list":self.dados["jogos"],
			"clube":self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now(),
			"calendario_epoca":self.dados["calendario_epoca"],
			"jogos_calendario":self.dados["jogos_calendario"]
		})
	
		return html
