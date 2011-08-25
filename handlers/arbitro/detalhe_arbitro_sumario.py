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

class DetalheArbitroSumario(DetalheArbitro):
		
	# memcache vars
	cache_namespace = "detalhe_arbitro_sumario"
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		dados = []

		# pode haver mais que um, por cada competicao
		acumuladores = AcumuladorCompeticao.all().filter("acuc_epoca = ", self.epoca).filter("acuc_versao = ", config.VERSAO_ACUMULADOR).filter("acuc_namespace = ", "arbitro")
		for acu in acumuladores:
						
			if acu.acuc_content["arbitro"].has_key(self.arbitro.key().id()):				
				top_arbitro = acu.acuc_content["arbitro"][self.arbitro.key().id()]
			
				dados.append({
					"epoca":acu.acuc_epoca,
					"competicao":acu.acuc_competicao,
					"jogos_realizados":top_arbitro["jr"],
					"cartoes_amarelos":top_arbitro["ca"],
					"cartoes_duplo_amarelos":top_arbitro["cda"],
					"cartoes_vermelhos":top_arbitro["cv"],
					"indisciplina":top_arbitro["ca"]+\
						1.5*top_arbitro["cda"]+\
						2*top_arbitro["cv"]
				})

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('arbitro','detalhe_arbitro_sumario.html', {
			"dados":self.dados,
			"arbitro":self.arbitro,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html