# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_clube import DetalheClube

class DetalheClubeJogadores(DetalheClube):
		
	# memcache vars
	cache_namespace = "detalhe_clube_jogadores"
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	def renderDados(self):
		dados = {}
		epoca_corrente = config.EPOCA_CORRENTE		

		acumulador = classes.getAcumuladorEpoca(self.epoca,
					config.VERSAO_ACUMULADOR, "jogador")
				
		jogadores = Jogador.all().filter("jgd_clube_actual = ", self.clube).order("jgd_nome").fetch(1000)	
		
		# o pickle tinha de vir num hash, portanto, o value é a lista
		top_jogadores = acumulador.acue_content["jogador"]

		dados["jogadores"] = []
		
		#logging.info(top_jogadores.keys())

		for jogador in jogadores:
			key = jogador.key().id()
			ctj = jogador.jgd_clubes.filter("ctj_epocas = ",epoca_corrente.key()).get()
			
			data = {"jogador":jogador,
			 "numero":ctj.ctj_numero if ctj else 0,
			 "posicao":jogador.jgd_posicao,
			 "jogos_realizados":0,
			 "minutos_jogados":0,
			 "golos_marcados":0,
			 "cartoes_amarelos":0,
			 "cartoes_duplo_amarelos":0,
			 "cartoes_vermelhos":0,
			 "indisciplina":0
			}
			
			#logging.info(key)
			
			if top_jogadores.has_key(key):
				
				# vamos ver as states mas só para quando o jogador esteve a jogar neste clube
				clu_id = self.clube.key().id()
				if top_jogadores[key].has_key(clu_id):
				
					if top_jogadores[key][clu_id].has_key("jr"):
						data["jogos_realizados"] =top_jogadores[key][clu_id]["jr"]
					if top_jogadores[key][clu_id].has_key("mj"):
						data["minutos_jogados"] =top_jogadores[key][clu_id]["mj"]
					if top_jogadores[key][clu_id].has_key("gm"):
						data["golos_marcados"] =top_jogadores[key][clu_id]["gm"]
					if top_jogadores[key][clu_id].has_key("ca"):
						data["cartoes_amarelos"] =top_jogadores[key][clu_id]["ca"]
					if top_jogadores[key][clu_id].has_key("cda"):
						data["cartoes_duplo_amarelos"] =top_jogadores[key][clu_id]["cda"]
					if top_jogadores[key][clu_id].has_key("cv"):
						data["cartoes_vermelhos"] =top_jogadores[key][clu_id]["cv"]

					data["indisciplina"] = top_jogadores[key][clu_id]["ca"] + 1.5*top_jogadores[key][clu_id]["cda"] + 2*top_jogadores[key][clu_id]["cv"]
								
			dados["jogadores"].append(data)
		return dados

	def renderHTML(self):
		
		html = self.render_subdir('clube','detalhe_clube_jogadores.html', {
			"jogadores":self.dados["jogadores"],
			"clube":self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html