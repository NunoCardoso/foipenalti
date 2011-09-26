# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from detalhe_clube import DetalheClube
from lib import gera_icc_para_jogo
from lib.detalhe_icc import DetalheICC

class DetalheClubeIndices(DetalheClube):
		
	# memcache vars
	cache_namespace = "detalhe_clube_indices"
	render_this_page_without_main = True

	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		
		# obter a lista de lances ordenadinhos
		lista_lances = Lance.gql("WHERE lan_epoca = :1 and lan_clubes = :2 ORDER by lan_data, lan_nome",  self.epoca, self.clube.key()).fetch(1000)

		# obter a fonte dos lances -- usar a época toda!
		acu_jornadas = {}
		acumuladores = AcumuladorJornada.all().filter("acuj_epoca = ", self.epoca).filter("acuj_versao = ", config.VERSAO_ACUMULADOR)
		for acu in acumuladores:
			acu_jornadas[acu.acuj_jornada.jor_nome] = acu.acuj_content
		
		detalhe_icc = DetalheICC()
		detalhe_icc.setLances(lista_lances)
		detalhe_icc.setClube(self.clube)
		detalhe_icc.setAcumuladoresJornadas(acu_jornadas)
		resultados = detalhe_icc.gera()
		
		jogos = resultados["jogos"]
		total_icc_beneficio = resultados["total_icc_beneficio"]
		total_icc_prejuizo = resultados["total_icc_prejuizo"]
		total_icc = (total_icc_beneficio + total_icc_prejuizo)
		
		return {"jogos":jogos, "total_icc_beneficio":total_icc_beneficio, 
			"total_icc_prejuizo":total_icc_prejuizo, "total_icc":total_icc}
		
	def renderHTML(self):
		
		html = self.render_subdir('clube','detalhe_clube_indices.html', {
			"detalhe_icc_dados":self.dados,
			"clube":self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html