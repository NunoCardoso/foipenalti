# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_clube import DetalheClube

class DetalheClubeSumario(DetalheClube):
		
	# memcache vars
	cache_namespace = "detalhe_clube_sumario"
	render_this_page_without_main = True

	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 
	
	def renderDados(self):
		
		dados = {}
		competicoes = []
		melhores_marcadores = []
		mais_indisciplinados = []
		
		top_list_melhores_marcadores = 5
		top_list_mais_indisciplinados = 5

		# primeiro, vamos saber quais são os jogadores deste clube
		# e fazer uma hash
		jgd_ids = []
		hash_jogadores = {}	
		clu_id = self.clube.key().id()
		jogadores = Jogador.all().filter("jgd_clube_actual = ", self.clube)

		for j in jogadores:
			jgd_id = j.key().id() 
			jgd_ids.append(jgd_id)
			hash_jogadores[jgd_id] = j

		acumulador = classes.getAcumuladorEpoca(self.epoca, 
			config.VERSAO_ACUMULADOR, "top_jogadores")
		
		if acumulador:
			top_jogadores = acumulador.acue_content["top_jogadores"]
			
			so_far = 0			
			for linha in top_jogadores["mais_golos"]:
				if linha["jgd"] in jgd_ids and so_far < top_list_melhores_marcadores: 
					# adiciona o obj a partir do id
					linha["jogador"] = hash_jogadores[linha["jgd"]]
					melhores_marcadores.append(linha)
					so_far += 1

			so_far = 0						
			for linha in top_jogadores["mais_cartoes"]:
				if linha["jgd"] in jgd_ids and so_far < top_list_mais_indisciplinados: 
					# adiciona o obj a partir do id
					linha["jogador"] = hash_jogadores[linha["jgd"]]
					mais_indisciplinados.append(linha)
					so_far += 1

			# total para as competições
			total_competicoes = {"jr":0, "vr":0, "er":0, "dr":0,
				"gmr":0, "gsr":0, "pr":0}
				
			for competicao in self.epoca.epo_competicoes:

				acuc = classes.getAcumuladorCompeticao(competicao,
					config.VERSAO_ACUMULADOR, "classificacao_real")

				if acuc:
					classificacao_total = acuc.acuc_content["classificacao_real"]["total"]

					for linha in classificacao_total:	
						if linha["clu"] == clu_id:
							competicoes.append({
								"competicao":competicao, 
								"stats":linha
							})
						
							total_competicoes["jr"] += linha["jr"]
							total_competicoes["vr"] += linha["vr"]
							total_competicoes["er"] += linha["er"]
							total_competicoes["dr"] += linha["dr"]
							total_competicoes["gmr"] += linha["gmr"]
							total_competicoes["gsr"] += linha["gsr"]
					
			dados = {"competicoes":competicoes,
			"total_competicoes":total_competicoes,
			"melhores_marcadores":melhores_marcadores,
			"mais_indisciplinados":mais_indisciplinados}

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('clube','detalhe_clube_sumario.html', {
			"competicoes":self.dados["competicoes"],
			"total_competicoes":self.dados["total_competicoes"],
			"melhores_marcadores":self.dados["melhores_marcadores"],
			"mais_indisciplinados":self.dados["mais_indisciplinados"],
			"clube":self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html