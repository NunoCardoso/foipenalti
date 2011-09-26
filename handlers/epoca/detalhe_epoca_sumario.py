# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from detalhe_epoca import DetalheEpoca

class DetalheEpocaSumario(DetalheEpoca):
		
	# memcache vars
	cache_namespace = "detalhe_epoca_sumario"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 

	# não há nada para devolver	
	def renderDados(self):

		competicoes = []
		melhores_marcadores = []
		mais_indisciplinados = []
					
		top_list_melhores_marcadores = 5
		top_list_mais_indisciplinados = 5
		
		# top jogadores: 
		acumulador = classes.getAcumuladorEpoca(self.epoca, 
			config.VERSAO_ACUMULADOR, "top_jogadores")
		
		top_jogadores = acumulador.acue_content["top_jogadores"]

		howmany = len(top_jogadores["mais_golos"]) if len(top_jogadores["mais_golos"]) <= top_list_melhores_marcadores else top_list_melhores_marcadores
		for linha in top_jogadores["mais_golos"][:howmany]:
			melhores_marcadores.append(linha)

		howmany = len(top_jogadores["mais_cartoes"]) if len(top_jogadores["mais_cartoes"]) <= top_list_mais_indisciplinados else top_list_mais_indisciplinados
		for linha in top_jogadores["mais_cartoes"][:howmany]:
			mais_indisciplinados.append(linha)

		# vamos recolher os ids de todos os jogadores
		ids = []
		for item in melhores_marcadores:
			# item = {jgd:1L, gol:1L}
			if not item["jgd"] in ids:
				ids.append(item["jgd"])
		for item in mais_indisciplinados:
			# item = {jgd:1L, crt:{ca:, cda: cv: tot:}}
			if not item["jgd"] in ids:
				ids.append(item["jgd"])
		
		# agora vamos obter os objectos, e fazer uma hash invertida.
		jogadores = Jogador.get_by_id(ids)
		jgds = {}
		for jogador in jogadores: 
			jgds[jogador.key().id()] = jogador
		
		# agora vamos substituir os ids pelos objectos
		for idx, val in enumerate(melhores_marcadores):
			melhores_marcadores[idx]["jogador"] = jgds[val["jgd"]]
		for idx, val in enumerate(mais_indisciplinados):
			mais_indisciplinados[idx]["jogador"] = jgds[val["jgd"]]
		
		for competicao in self.epoca.epo_competicoes:

			acumulador = classes.getAcumuladorCompeticao(competicao, 
				config.VERSAO_ACUMULADOR, "classificacao_real")
			
			classificacao_total = None
				
			if acumulador and acumulador.acuc_content.has_key("classificacao_real"):
				classificacao_total = acumulador.acuc_content["classificacao_real"]["total"]
			# vamos tirar a linha que interessa...
			
			competicoes.append({
				"competicao":competicao, 
				"dados":classificacao_total[0] if classificacao_total else None,
				"clube":Clube.get_by_id(classificacao_total[0]["clu"]) if classificacao_total else None
			})
					
		dados = {"competicoes":competicoes,
					"melhores_marcadores":melhores_marcadores,
					"mais_indisciplinados":mais_indisciplinados}

		return dados

	def renderHTML(self):
		
		epoca_corrente = False
		if config.EPOCA_CORRENTE == self.epoca:
			epoca_corrente = True
			
		html = self.render_subdir('epoca','detalhe_epoca_sumario.html', {
			"competicoes":self.dados["competicoes"],
			"melhores_marcadores":self.dados["melhores_marcadores"],
			"mais_indisciplinados":self.dados["mais_indisciplinados"],
			"epoca":self.epoca,
			"epoca_corrente":epoca_corrente,
			"data":datetime.datetime.now()
		})
		return html