# -*- coding: utf-8 -*-

from google.appengine.api import memcache

import logging
import re
import config 
import datetime
import sys
import classes
import listas
import acumulador

from classes import * #Lance
from classificacao import Classificacao
from tabela_icc import TabelaICC
from grafico_icc import GraficoICC
from grafico_ica import GraficoICA
from copy import deepcopy

def doit(content, stats):
	
		# key = id do elemento, values = hash com coisas
		for key1, value1 in content.items():
			
			# não há árbitro -> bulkload
			if not stats.has_key(key1):

				stats[key1] = value1
				
			else:
				
				# key2 = propriedade, value2 = int ou hash de propriedades
				for key2, value2 in value1.items():
					
					if not stats[key1].has_key(key2):

						stats[key1][key2] = value2
					
					else:
						# hash: vamos com calma, elementos tipo jogador_amarelos
						if type(value2) == type({}):
						
							for key3, value3 in value2.items():

								if not stats[key1][key2].has_key(key3):

									stats[key1][key2][key3] = value3

								else:
									if type(value3) == type({}):
							
										for key4, value4 in value3.items():
									
											if stats[key1][key2][key3].has_key(key4):
								
												stats[key1][key2][key3][key4] += value4
											else:
												stats[key1][key2][key3][key4] = value4
							
									else:
								
										if stats[key1][key2].has_key(key3):
								
											stats[key1][key2][key3] += value3
										else:
											stats[key1][key2][key3] = value3
						
						else:
							# simple integer/long, let's add.
							stats[key1][key2] += value2
	
# devolve acumuladores para cada competição, 
# os  elementos: jogador, clube, arbitro, jogo, lance
def gera(competicao, acuc_basico, 
				acuc_classificacao, acuc_tabela_icc, acuc_icc, acuc_top_arbitros,
				acuc_top_jogos, acuc_top_jogadores, acuc_top_clubes):

	stats_parcial = [] # as a list, I have jornadas ordered
	
	if acuc_basico == "on":
		logging.info("acuc_basico está on, vou gerar arbitro, jogador, clube e jogo a partir das estatísticas")

		acumulador_jornadas = AcumuladorJornada.all().filter("acuj_competicao = ", competicao).filter("acuj_versao = ", config.VERSAO_ACUMULADOR).fetch(1000)
		acumulador_jornadas = sorted(acumulador_jornadas, cmp=lambda x,y: cmp(x.acuj_jornada.jor_ordem, y.acuj_jornada.jor_ordem))

		stats_total = {
			"arbitro":{},
			"jogo": {},
			"jogador":{},
			"clube":{}
		}	
		
		for ac in acumulador_jornadas:
			
			parcial = {
				"arbitro":{},
				"jogo": {},
				"jogador":{},
				"clube":{},
				"jornada":ac.acuj_jornada
			}	
				
			# depicle it
			content = ac.acuj_content
		
			logging.info(u"acumulador_competicao: a ler dados do acumulador_jornada %s " % ac.acuj_jornada.__str__())

			doit(content["arbitro"], stats_total["arbitro"])
			doit(content["jogador"], stats_total["jogador"])
			doit(content["jogo"], stats_total["jogo"])		
			doit(content["clube"], stats_total["clube"])
			
			# save copies to the parcial_stats
			parcial["clube"] = deepcopy(stats_total["clube"])
			parcial["arbitro"] = deepcopy(stats_total["arbitro"])
			parcial["jogo"] = deepcopy(stats_total["jogo"])
		#	parcial["jogador"] = deepcopy(stats_total["jogador"])
			stats_parcial.append(parcial)
			
	else:
		
		# não permite parciais, a não ser que os grave, mas como não estou a fazer isso...
		logging.info("acuc_basico está off, vou gerar arbitro, jogador, clube e jogo a partir do acumulador")

		acumuladorcompeticoes = AcumuladorCompeticao.all().filter("acuc_competicao = ", competicao).filter("acuc_versao = ", config.VERSAO_ACUMULADOR)
		stats_total = {}
		
		# teoricamente, só há uma competição
		for acu in acumuladorcompeticoes:
		
			if acu.acuc_namespace == "arbitro":
				stats_total["arbitro"] = acu.acuc_content["arbitro"]
			if acu.acuc_namespace == "clube":
				stats_total["clube"] = acu.acuc_content["clube"]
			if acu.acuc_namespace == "jogador":
				stats_total["jogador"] = acu.acuc_content["jogador"]
			if acu.acuc_namespace == "jogo":
				stats_total["jogo"] = acu.acuc_content["jogo"]

#####################
### CLASSIFICACAO ###
#####################
	
	if acuc_classificacao == "on":
		# passar o objecto de classificação deve servir só para saber quais as 
		# regras de ordenação da classificação. Não usar os dados dos jogos!!!

		tabela_real = None
		tavela_virtual = None
		
		if competicao.cmp_tipo == "Liga":
			tabela_real, tabela_virtual =  Classificacao().gera_classificacao_liga(competicao, stats_parcial, stats_total)

		elif competicao.cmp_tipo == "TacaPortugal":
			tabela_real, tabela_virtual =  Classificacao().gera_classificacao_taca(competicao, stats_parcial, stats_total)

		elif competicao.cmp_tipo == "TacaLiga":
			tabela_real, tabela_virtual =  Classificacao().gera_classificacao_taca(competicao, stats_parcial, stats_total)

		elif competicao.cmp_tipo == "SuperTaca":
			tabela_real, tabela_virtual =  Classificacao().gera_classificacao_taca(competicao, stats_parcial, stats_total)

		stats_total["classificacao_real"] = tabela_real
		stats_total["classificacao_virtual"] = tabela_virtual

##################
### TABELA ICC ###
##################
	
	# independentemente de ser para Liga ou não, isto é só para clubes da Liga
	# se não houver liga ,não faz mal... vai tudo
	# se não houver nada (= início época), deixa ir nada.
	
	liga = competicao.cmp_epoca.epo_competicoes.filter("cmp_tipo = ","Liga").get()
	ac = classes.getAcumuladorCompeticao(liga, config.VERSAO_ACUMULADOR, "clube")
	clubes_liga_ids = None
	
	if ac:
		clubes_liga_ids = ac.acuc_content["clube"].keys()
	else:
		ac = classes.getAcumuladorCompeticao(competicao, config.VERSAO_ACUMULADOR, "clube")
		if ac:
			clubes_liga_ids = ac.acuc_content["clube"].keys()
	
	# se não há nada (= início época), vamos ao cjc
	if not clubes_liga_ids:
		clubes = [] 
		cjcs = ClubeJogaCompeticao.all().filter("cjc_competicao = ", liga)
		for cjc in cjcs:
			clubes.append(cjc.cjc_clube)
	else:
		clubes = Clube.get_by_id(clubes_liga_ids)

	clubes = sorted(clubes, cmp=lambda x,y: cmp(x.clu_numero_visitas, y.clu_numero_visitas), reverse=True)
	
	if acuc_tabela_icc == "on":
		# vamos assumir que sabemos que queremos uma tabela icc / Liga
		stats_total["tabela_icc"] = TabelaICC.gera_nova_tabela_icc(stats_total, clubes)

###########
### ICC ###
###########
	
	if acuc_icc == "on":
		# vamos assumir que sabemos que queremos uma tabela icc / Liga
		arbitros = Arbitro.all().fetch(1000)
		stats_total["icc"] = GraficoICC.gera_novo_grafico_icc(stats_total, stats_parcial, clubes)
		stats_total["ica"] = GraficoICA.gera_novo_grafico_ica(stats_total, stats_parcial, arbitros)
		
############
### TOPS ###
############
	
	if acuc_top_clubes == "on":
		stats_total["top_clubes"] = acumulador.gera_top_clubes(stats_total)
	if acuc_top_arbitros == "on":
		stats_total["top_arbitros"] = acumulador.gera_top_arbitros(stats_total)
	if acuc_top_jogadores == "on":
		stats_total["top_jogadores"] = acumulador.gera_top_jogadores(stats_total, competicao)
	if acuc_top_jogos == "on":
		stats_total["top_jogos"] = acumulador.gera_top_jogos(stats_total)

	return stats_total
	


