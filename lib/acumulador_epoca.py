# -*- coding: utf-8 -*-

from google.appengine.api import memcache

import logging
import re
import config 
import datetime
import sys
import classes
import acumulador

from classes import * #Lance
from tabela_icc import TabelaICC
from grafico_icc import GraficoICC
from grafico_ica import GraficoICA
import listas

# este do_id tem que lidar com hashes, e também com listas ordenadas
# content = conteúdo de cada competicao. stats = hash que vai somando os valores
# namespace é importante, para identificar o que são os ids no merge de arrays
def doit(content, stats, namespace):
	
		# key = id do elemento, values = hash com coisas
		for key1, value1 in content.items():
			
			# não há elemento -> adicionar hash com coisas
			if not stats.has_key(key1):

				stats[key1] = value1
				
			else:
				
				if type(value1) == type({}):

					# key2 = propriedade, value2 = int ou hash de propriedades
					for key2, value2 in value1.items():
					
						# não há elemento -> adicionar hash com coisas
						if not stats[key1].has_key(key2):

							stats[key1][key2] = value2
					
						else:
							# hash: vamos com calma, elementos tipo jogador_amarelos
						
							if type(value2) == type({}):
						
								for key3, value3 in value2.items():
								
									# não há elemento -> adicionar hash com coisas
									if not stats[key1][key2].has_key(key3):
									
										stats[key1][key2][key3] = value3

									else:
										
										if type(value3) == type({}):
							
											# a este nível, vamos assumir que value4 
											# não é estrutura, deve ser int ou long apenas 
											for key4, value4 in value3.items():
									
												if not stats[key1][key2][key3].has_key(key4):

													stats[key1][key2][key3][key4] = value4

												else:

													stats[key1][key2][key3][key4] += value4
							
										elif type(value3) == type([]):

											logging.info("Value 3... nunca devia ocorrer!")

										else:
											
											# value3 é um int/long
											if not stats[key1][key2].has_key(key3):

												stats[key1][key2][key3] = value3

											else:

												stats[key1][key2][key3] += value3
						
							elif type(value2) == type([]):

								logging.info("Value 2... nunca defia ocorrer!")

							else:
								# value2 is simple integer/long, let's add.
								if not stats[key1].has_key(key2):

									stats[key1][key2] = value2

								else:

									stats[key1][key2] += value2
	
				elif type(value1) == type([]): 
					
					# logging.info("value1")
					# logging.info(value1)
					# logging.info("stats[key1]")
					# logging.info(stats[key1])
					
					merged_list = []
					merger_hash = {}
					
					# os elementos que a lista tem são hashes simples
					# (tipo {"jgd":1L, "gol":1}) , ou hash com hash 
					# (tipo {"jgd":1L, "crt":{"tot":x, "ca":X, "cda":x, "cv":x}})
					
					# tenho de saber quais são os ids ("jgd", "clu", "arb", "jog", "lan")
					# e quais são as quantidades 
					# ("gol", "p", "crt"->"tot", "num", "dif", "icc", etc)
					
					# value1 é sempre uma LISTA, vem de content (each competição)
					# stats[key1] é também uma lista, é a lista de itens já acumulados até agora

					# objectivo: criar uma hash nova usando os elementos de stats[key1], 
					# depois somar-lhe os elementos da hash usando os elementos de value1
					
					for elem in stats[key1]:
						
						id = None
						id_name = None
						
						if namespace == "top_jogadores":
							id = elem["jgd"]
						if namespace == "top_clubes":
#							logging.info(elem)
							id = elem["clu"]
						if namespace == "top_arbitros":
							id = elem["arb"]
						if namespace == "top_jogos":
							id = elem["jog"]
						merger_hash[id] = elem
					
					# merge: detectar ids para saber que são para usar como key na merger_hash, 
					# e saber que não são para acumular como se fossem propriedades
					
					for elem in value1:
					
						id = None
						id_name = None
						if namespace == "top_jogadores":
							id_name = "jgd"
						if namespace == "top_clubes":
							id_name = "clu"
						if namespace == "top_arbitros":
							id_name = "arb"
						if namespace == "top_jogos":
							id_name = "jog"

						id = elem[id_name]
						
						# novo elemento - só adicionar	
						if not merger_hash.has_key(id):

							merger_hash[id] = elem
						
						# elemento existente - fazer merge: 
						else:
							for elem_key, elem_value in elem.items():
								
								# se o elem_key não é o id, mas sim propriedades acumuláveis... 
								if not elem_key == id_name:
									
									# se o elem_value é uma hash (cartões):
									if type(elem_value) == type({}): 
										
										for elem2_key, elem2_value in elem_value.items():
										
											# se o elem_key já existe ou não
											if not merger_hash[id][elem_key].has_key(elem2_key):
												# merger_hash[1L]["crt"]["cda"] = 1L
												merger_hash[id][elem_key][elem2_key] = elem2_value
											else:
												merger_hash[id][elem_key][elem2_key] += elem2_value
										
									# se o elem_value é um valor (int/long)
									else:
										# se o elem_key já existe ou não
										if not merger_hash[id].has_key(elem_key):
											merger_hash[id][elem_key] = elem_value
										else:
											merger_hash[id][elem_key] += elem_value
					
					# sort: by property type
					if key1 == "cartoes_mostrados" or key1 == "mais_cartoes" or key1 == "mais_indisciplina":
						# uso os merged_hash.values(), porque já tem o id...
						merged_list = sorted(merger_hash.values(), cmp=lambda x,y: \
							cmp(x["crt"]["tot"], y["crt"]["tot"] ), reverse=True )
	
					elif key1 == "mais_icc":
						merged_list = sorted(merger_hash.values(), cmp=lambda x,y: \
							cmp(x["icc"], y["icc"]), reverse=True )
					
					elif key1.startswith("mais_golos") or key1 == "saldo_golos":
						merged_list = sorted(merger_hash.values(), cmp=lambda x,y: \
							cmp(x["gol"], y["gol"]), reverse=True )
					
					elif key1.startswith("mais_pontos") or key1 == "saldo_pontos":
						merged_list = sorted(merger_hash.values(), cmp=lambda x,y: \
							cmp(x["p"], y["p"]), reverse=True )
					
					elif key1 == "maiores_goleadas":
						merged_list = sorted(merger_hash.values(), cmp=lambda x,y: \
							cmp(x["dif"], y["dif"]), reverse=True )
					
					elif key1 == "mais_lances":
							merged_list = sorted(merger_hash.values(), cmp=lambda x,y: \
							cmp(x["num"], y["num"]), reverse=True )
					 
					# logging.info("merged_list")
					# logging.info(merged_list)

					stats[key1] = merged_list

	
# devolve acumuladores para cada competição, 
# os  elementos: jogador, clube, arbitro, jogo, lance
def gera(epoca, acue_basico, 
				acue_tabela_icc, acue_icc, acue_top_arbitros,
				acue_top_jogos, acue_top_jogadores, acue_top_clubes):

	acuc = AcumuladorCompeticao.all().filter("acuc_epoca = ", epoca).filter("acuc_versao = ", config.VERSAO_ACUMULADOR).fetch(1000)

	stats = {}
	
	if acue_basico == "on":
		logging.info("acue_basico está on, vou gerar arbitro, jogador, clube e jogo a partir das estatísticas")

		stats = {
			"arbitro":{},
			"jogo": {},
			"jogador":{},
			"clube":{},
			"top_arbitros":{},
			"top_jogos": {},
			"top_jogadores":{},
			"top_clubes":{}
		}	
		for ac in acuc:
		
			# depicle it
			content = ac.acuc_content
		
			logging.info(u"acumulador_epoca: a ler dados do acumulador_competicao %s " % ac.acuc_competicao.__str__())

			if (ac.acuc_namespace == "arbitro"):
				doit(content["arbitro"], stats["arbitro"], "arbitro")
			if (ac.acuc_namespace == "jogador"):
				doit(content["jogador"], stats["jogador"], "jogador")
			if (ac.acuc_namespace == "jogo"):
				doit(content["jogo"], stats["jogo"], "jogo")		
			if (ac.acuc_namespace == "clube"):
				doit(content["clube"], stats["clube"], "clube")
			

	else:
		logging.info("acue_basico está off, vou gerar arbitro, jogador, clube e jogo a partir do acumulador")

		acumuladorepocas = AcumuladorEpoca.all().filter("acue_epoca = ", epoca).filter("acue_versao = ", config.VERSAO_ACUMULADOR)
		
		stats_total = {}
		stats = {}
		
		for acu in acumuladorepocas:
		
			if acu.acue_namespace == "arbitro":
				stats["arbitro"] = acu.acue_content["arbitro"]
			if acu.acue_namespace == "clube":
				stats["clube"] = acu.acue_content["clube"]
			if acu.acue_namespace == "jogador":
				stats["jogador"] = acu.acue_content["jogador"]
			if acu.acue_namespace == "jogo":
				stats["jogo"] = acu.acue_content["jogo"]
				
##############
### TABELA ICC ###
##############

	liga = epoca.epo_competicoes.filter("cmp_tipo = ","Liga").get()

	ac = classes.getAcumuladorCompeticao(liga, config.VERSAO_ACUMULADOR, "clube")
	if ac:
		clubes_liga_ids = ac.acuc_content["clube"].keys()
	else:
		ac = classes.getAcumuladorEpoca(epoca, config.VERSAO_ACUMULADOR, "clube")
		clubes_liga_ids = ac.acue_content["clube"].keys()
		
	clubes = Clube.get_by_id(clubes_liga_ids)
	clubes = sorted(clubes, cmp=lambda x,y: cmp(x.clu_numero_visitas, y.clu_numero_visitas), reverse=True)
	
	if acue_tabela_icc == "on":
		# vamos assumir que sabemos que queremos uma tabela icc / Liga
		stats["tabela_icc"] = TabelaICC.gera_nova_tabela_icc(stats, clubes)

###########
### ICC ###
###########
	
	if acue_icc == "on":
		# vamos assumir que sabemos que queremos uma tabela icc / Liga
		arbitros = Arbitro.all().fetch(1000)
		stats["icc"] = GraficoICC.gera_novo_grafico_icc(stats, {}, clubes)
		stats["ica"] = GraficoICA.gera_novo_grafico_ica(stats, {}, arbitros)

############
### TOPS ###
############

# os tops podem ser aglotinações de hashes das competições, não é preciso regerar
	
	
	for ac in acuc:
		
		if acue_top_clubes == "on" and ac.acuc_namespace == "top_clubes":
				doit(ac.acuc_content["top_clubes"], stats["top_clubes"], "top_clubes")
		if acue_top_arbitros == "on" and ac.acuc_namespace == "top_arbitros":
				doit(ac.acuc_content["top_arbitros"], stats["top_arbitros"], "top_arbitros")
		if acue_top_jogadores == "on" and ac.acuc_namespace == "top_jogadores":
				doit(ac.acuc_content["top_jogadores"], stats["top_jogadores"], "top_jogadores")
		if acue_top_jogos == "on" and ac.acuc_namespace == "top_jogos":
				doit(ac.acuc_content["top_jogos"], stats["top_jogos"], "top_jogos")

	return stats