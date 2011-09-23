# -*- coding: utf-8 -*-

import logging
import re
import config 
import datetime
import sys

from classes import *

class Classificacao(): 

	competicao = None
	
	# pequena ordenação dos jogos, pelo clube1, para aceder facilmente à info 
	# de jogos entre dois clubes, no desempate de classificações
	jogos_by_clube1 = {}
	
	# devia ser:
	# 1º pontos, 2º pontos entre eles, 3º diferença golos entre eles, 4º nº golos marcados entre eles, 5º diferença de golos geral
	# 6º numero de golos marcados geral

	def cmp_liga_classificacao_real(self, it1, it2):
		# 1º pontos
		#logging.info(it1)
		#logging.info(it2)
		result = cmp(it1['pr'], it2['pr'])
		if result != None and result != 0:
			return result
		else:
			# entre eles
			clube1 = Clube.get_by_id(it1["clu"])
			clube2 = Clube.get_by_id(it2["clu"])
			
			jogo1 = None
			jogo2 = None
			
			if self.jogos_by_clube1.has_key(it1["clu"]):
				for j in self.jogos_by_clube1[it1["clu"]]:
					if j.jog_clube2 == clube2:
						jogo1 = j
					
			if self.jogos_by_clube1.has_key(it2["clu"]):
				for j in self.jogos_by_clube1[it2["clu"]]:
					if j.jog_clube2 == clube1:
						jogo2 = j
			
			if jogo1 or jogo2:
				marcados_clube1 = 0
				marcados_clube2 = 0
				pontos_clube1 = 0
				sofridos_clube1 = 0
				sofridos_clube2 = 0
				pontos_clube2 = 0
				
				if jogo1 and jogo1.jog_golos_clube1 != None and jogo1.jog_golos_clube2 != None and jogo1.jog_golos_virtuais_clube1 != None and jogo1.jog_golos_virtuais_clube2 != None:
					marcados_clube1 += jogo1.jog_golos_clube1
					marcados_clube2 += jogo1.jog_golos_clube2
					sofridos_clube1 += jogo1.jog_golos_clube2
					sofridos_clube2 += jogo1.jog_golos_clube1
					if jogo1.jog_golos_clube1 > jogo1.jog_golos_clube2:
						pontos_clube1 += 3
					if jogo1.jog_golos_clube1 < jogo1.jog_golos_clube2:
						pontos_clube2 += 3
					if jogo1.jog_golos_clube1 == jogo1.jog_golos_clube2:
						pontos_clube1 += 1
						pontos_clube2 += 1
				
				# para o segundo jogo, os clubes trocam de posição: o clube1 é o que no jogo é representado por clube2		
				if jogo2 and jogo2.jog_golos_clube1 != None and jogo2.jog_golos_clube2 != None and jogo2.jog_golos_virtuais_clube1 != None and jogo2.jog_golos_virtuais_clube2 != None:
					marcados_clube1 += jogo2.jog_golos_clube2
					marcados_clube2 += jogo2.jog_golos_clube1
					sofridos_clube1 += jogo2.jog_golos_clube1
					sofridos_clube2 += jogo2.jog_golos_clube2
					if jogo2.jog_golos_clube2 > jogo2.jog_golos_clube1:
						pontos_clube1 += 3
					if jogo2.jog_golos_clube2 < jogo2.jog_golos_clube1:
						pontos_clube2 += 3
					if jogo2.jog_golos_clube2 == jogo2.jog_golos_clube1:
						pontos_clube1 += 1
						pontos_clube2 += 1
				
				# 2º - pontos entre eles
				result = cmp(pontos_clube1, pontos_clube2)
#				logging.info(u"2º: %s para %s %s" % (str(result),clube1.clu_nome_curto,clube2.clu_nome_curto))
#				logging.info(u"pontos: %s %s" % (str(pontos_clube1),str(pontos_clube2)) )

				if result != None and result != 0:
					return result
				else:
				# 3º diferença de golos entre eles
					result = cmp(marcados_clube1 - sofridos_clube1, marcados_clube2 - sofridos_clube2)
					
					if result != None and result != 0:
						return result
					else:
					# 4º nº de golos marcados entre eles
						result = cmp(marcados_clube1, marcados_clube2)
					
						if result != None and result != 0:
							return result
						else:
							# 5º diferença de golos geral 
							result = cmp(it1['gmr']-it1['gsr'], 
							it2['gmr']-it2['gsr'])
							if result != None and result != 0:
								return result
							else:
      						#6º número de golos marcados geral
								result = cmp(it1['gmr'], it2['gmr'])
								if result != None and result != 0:
									return result
								else:
									return 0
			else:
				# 5º diferença de golos geral 
				result = cmp(it1['gmr']-it1['gsr'], 
					it2['gmr']-it2['gsr'])
				if result != None and result != 0:
					return result
				else:
      			#6º número de golos marcados geral
					result = cmp(it1['gmr'], it2['gmr'])
					if result != None and result != 0:
						return result
					else:
						return 0

	def cmp_liga_classificacao_virtual(self, it1, it2):
		# 1º pontos
		result = cmp(it1['pv'], it2['pv'])
		if result != None and result != 0:
			return result
		else:
			# entre eles
			clube1 = Clube.get_by_id(it1["clu"])
			clube2 = Clube.get_by_id(it2["clu"])
			
			jogo1 = None
			jogo2 = None
			
			if self.jogos_by_clube1.has_key(it1["clu"]):
				for j in self.jogos_by_clube1[it1["clu"]]:
					if j.jog_clube2 == clube2:
						jogo1 = j
					
			if self.jogos_by_clube1.has_key(it2["clu"]):
				for j in self.jogos_by_clube1[it2["clu"]]:
					if j.jog_clube2 == clube1:
						jogo2 = j
			
			if jogo1 or jogo2:
				marcados_clube1 = 0
				marcados_clube2 = 0
				pontos_clube1 = 0
				sofridos_clube1 = 0
				sofridos_clube2 = 0
				pontos_clube2 = 0
				
				if jogo1 and jogo1.jog_golos_clube1 != None and jogo1.jog_golos_clube2 != None and jogo1.jog_golos_virtuais_clube1 != None and jogo1.jog_golos_virtuais_clube2 != None:

					marcados_clube1 += jogo1.jog_golos_virtuais_clube1
					marcados_clube2 += jogo1.jog_golos_virtuais_clube2
					sofridos_clube1 += jogo1.jog_golos_virtuais_clube2
					sofridos_clube2 += jogo1.jog_golos_virtuais_clube1
					if jogo1.jog_golos_virtuais_clube1 > jogo1.jog_golos_virtuais_clube2:
						pontos_clube1 += 3
					if jogo1.jog_golos_virtuais_clube1 < jogo1.jog_golos_virtuais_clube2:
						pontos_clube2 += 3
					if jogo1.jog_golos_virtuais_clube1 == jogo1.jog_golos_virtuais_clube2:
						pontos_clube1 += 1
						pontos_clube2 += 1
										
				# para o segundo jogo, os clubes trocam de posição: o clube1 é o que no jogo é representado por clube2		
				if jogo2 and jogo2.jog_golos_clube1 != None and jogo2.jog_golos_clube2 != None and jogo2.jog_golos_virtuais_clube1 != None and jogo2.jog_golos_virtuais_clube2 != None:
					marcados_clube1 += jogo2.jog_golos_virtuais_clube2
					marcados_clube2 += jogo2.jog_golos_virtuais_clube1
					sofridos_clube1 += jogo2.jog_golos_virtuais_clube1
					sofridos_clube2 += jogo2.jog_golos_virtuais_clube2

					if jogo2.jog_golos_virtuais_clube2 > jogo2.jog_golos_virtuais_clube1:
						pontos_clube1 += 3
					if jogo2.jog_golos_virtuais_clube2 < jogo2.jog_golos_virtuais_clube1:
						pontos_clube2 += 3
					if jogo2.jog_golos_virtuais_clube2 == jogo2.jog_golos_virtuais_clube1:
						pontos_clube1 += 1
						pontos_clube2 += 1
				
				# 2º - pontos entre eles
				result = cmp(pontos_clube1, pontos_clube2)
				if result != None and result != 0:
					return result
				else:
				# 3º diferença de golos entre eles
					result = cmp(marcados_clube1 - sofridos_clube1, marcados_clube2 - sofridos_clube2)
					
					if result != None and result != 0:
						return result
					else:
					# 4º nº de golos marcados entre eles
						result = cmp(marcados_clube1, marcados_clube2)
					
						if result != None and result != 0:
							return result
						else:
							# 5º diferença de golos geral 
							result = cmp(it1['gmv']-it1['gsv'], 
							it2['gmv']-it2['gsv'])
							if result != None and result != 0:
								return result
							else:
      						#6º número de golos marcados geral
								result = cmp(it1['gmv'], it2['gmv'])
								if result != None and result != 0:
									return result
								else: 
									return 0
			else:
				# 5º diferença de golos geral 
				result = cmp(it1['gmv']-it1['gsv'], 
					it2['gmv']-it2['gsv'])
				if result != None and result != 0:
					return result
				else:
					#6º número de golos marcados geral
					result = cmp(it1['gmv'], it2['gmv'])
					if result != None and result != 0:
						return result
					else:
						return 0


	def cmp_taca_classificacao_real(self, it1, it2):

		
		# de reparar que it2 vem primeiro - quanto maior a jor_ordem, melhor
		result = cmp(it2['jo'], it1['jo'])
		if result != None and result != 0:
			#logging.info(u"1º: %s para %s %s" % (str(result),it2['jo'], it1['jo']))
			
			return result
		else:
			
			# entre eles
			clube1 = Clube.get_by_id(it1["clu"])
			clube2 = Clube.get_by_id(it2["clu"])
			
			jogo1 = None
			jogo2 = None
			
			if self.jogos_by_clube1.has_key(it1["clu"]):
				for j in self.jogos_by_clube1[it1["clu"]]:
					if j.jog_clube2 == clube2:
						jogo1 = j
					
			if self.jogos_by_clube1.has_key(it2["clu"]):
				for j in self.jogos_by_clube1[it2["clu"]]:
					if j.jog_clube2 == clube1:
						jogo2 = j

			if jogo1 or jogo2:
				marcados_clube1 = 0
				marcados_clube2 = 0
				pontos_clube1 = 0
				sofridos_clube1 = 0
				sofridos_clube2 = 0
				pontos_clube2 = 0
				
				if jogo1 and jogo1.jog_golos_clube1 != None and jogo1.jog_golos_clube2 != None and jogo1.jog_golos_virtuais_clube1 != None and jogo1.jog_golos_virtuais_clube2 != None:
					marcados_clube1 += jogo1.jog_golos_clube1
					marcados_clube2 += jogo1.jog_golos_clube2
					sofridos_clube1 += jogo1.jog_golos_clube2
					sofridos_clube2 += jogo1.jog_golos_clube1
					if jogo1.jog_golos_clube1 > jogo1.jog_golos_clube2:
						pontos_clube1 += 3
					if jogo1.jog_golos_clube1 < jogo1.jog_golos_clube2:
						pontos_clube2 += 3
					if jogo1.jog_golos_clube1 == jogo1.jog_golos_clube2:
						pontos_clube1 += 1
						pontos_clube2 += 1
				
				# para o segundo jogo, os clubes trocam de posição: o clube1 é o que no jogo é representado por clube2		
				if jogo2 and jogo2.jog_golos_clube1 != None and jogo2.jog_golos_clube2 != None and jogo2.jog_golos_virtuais_clube1 != None and jogo2.jog_golos_virtuais_clube2 != None:
					marcados_clube1 += jogo2.jog_golos_clube2
					marcados_clube2 += jogo2.jog_golos_clube1
					sofridos_clube1 += jogo2.jog_golos_clube1
					sofridos_clube2 += jogo2.jog_golos_clube2
					if jogo2.jog_golos_clube2 > jogo2.jog_golos_clube1:
						pontos_clube1 += 3
					if jogo2.jog_golos_clube2 < jogo2.jog_golos_clube1:
						pontos_clube2 += 3
					if jogo2.jog_golos_clube2 == jogo2.jog_golos_clube1:
						pontos_clube1 += 1
						pontos_clube2 += 1
				
				# 2º - pontos entre eles
				result = cmp(pontos_clube2, pontos_clube1)
				#logging.info(u"2º: %s para %s %s" % (str(result),clube2.clu_nome_curto,clube1.clu_nome_curto))
				#logging.info(u"pontos: %s %s" % (str(pontos_clube2),str(pontos_clube1)) )

				if result != None and result != 0:
			
					# pequeno hack: se for uma final, 
					# mudar os nomes para "Vencedor" e "finalista"
					if it2['jn'] == "Final" and it1['jn'] == "Final":
						if result < 0: 
							it1['jn'] = "Vencedor"
							it2['jn'] = "Finalista"
						else:
							it2['jn'] = "Vencedor"
							it1['jn'] = "Finalista"
				
					return result
			
			else:
				# 3º diferença de golos geral 
				result = cmp(it2['gmv']-it2['gsv'], 
					it1['gmv']-it1['gsv'])
	#			logging.info(u"3º: %s para %s %s" % (str(result),clube1.clu_nome_curto,clube2.clu_nome_curto))

				if result != None and result != 0:
					return result
				else:
					#4º número de golos marcados geral
					result = cmp(it2['gmv'], it1['gmv'])
					#logging.info(u"4º: %s para %s %s" % (str(result),clube1.clu_nome_curto,clube2.clu_nome_curto))
					if result != None and result != 0:
						return result
					else:
						return 0
					
		# se tudo falha...
		#logging.info(u"Xº: 0 para %s %s" % (clube1.clu_nome_curto,clube2.clu_nome_curto))

		return 0
		
	# gera objectos para colocar no namespace "classificacao_real", "classificacao_virtual"
	# no AcumuladorCompeticao
	def gera_classificacao_liga(self, competicao, stats_parcial, competicao_hash):
	
		logging.info("Gerando a classificação da competicao "+competicao.__str__())
		
		# stats_parcial é uma lista, ordenada por ordem de jornada, que tem uma hash:
		# {"clube":xxx, "jornada":jornada, "XXX":XXX} 
		# ou seja, tem imagens parciais do stats_total (ou competicao_hash, aqui)
		
		# assim posso calcular a classificação parcial a cada jornada.
		# se for à competição_hash, posso ir ao acumulador de clubes e tenho já o 
		# total de golos, pontos, etc.
		
		# Vou usar o acumulador_jornada para os parciais, e o competicao_hash para o total
		
# O AcumuladorCompeticao deve ter a seguinte estrutura de classificação, para cada um dos 
# itens "classificao_real" e "classificacao_parcial":

#	{"total":
#		[{"clube":key1,"posicao_real":1, etc}, 
#		 {"clube":key2,"posicao_real":2, etc},
#		 {"..."}], 
#	 "parcial":
#		[{"jornada":jornada1, "classificacao_parcial":
#			[{"clube":key1,"posicao_real":1, etc},
#			 {"clube":key2,"posicao_real":2, etc},
#			 {"..."}] },
#		 {"jornada":jornada2, "classificacao_parcial":
#			[{"clube":key1,"posicao_real":1, etc},
#			 {"clube":key2,"posicao_real":2, etc},
#			 {"..."}] },
#		 {...}]
#  }

		self.competicao = competicao
		jogos = Jogo.all().filter("jog_competicao = ", self.competicao).fetch(1000)

		for jogo in jogos:
			if jogo.jog_clube1 != None and jogo.jog_clube2 != None:
				if not self.jogos_by_clube1.has_key(jogo.jog_clube1.key().id()):
					self.jogos_by_clube1[jogo.jog_clube1.key().id()] = []
				self.jogos_by_clube1[jogo.jog_clube1.key().id()].append(jogo)
		
		tabela_ordenada_real = {"total":[], "parcial":[]}
		tabela_ordenada_virtual = {"total":[], "parcial":[]}

		tabela_total = {}
		
		# classificacao TOTAL, se houver jogos jogados na competição (= já há a key clube com coisas lá)
		for cjc in competicao.cmp_clubes:
			clube_id = cjc.cjc_clube.key().id()
			tabela_total[clube_id] = {
				"clu":clube_id,
				"psr":0, "psv":0, 
				"jr":0, "vr":0, "vv":0, "er": 0, "ev":0, 
				"dr":0, "dv":0, "gmr":0, "gmv":0, "gsr":0,
				"gsv":0, "pr":0, "pv":0
			}
				
		if competicao_hash["clube"]:		
			for key, value in competicao_hash["clube"].items():
				tabela_total[key] = {
					"clu":key,
					"psr":0, "psv":0, 
					"jr":competicao_hash["clube"][key]["jr"],
					"vr":competicao_hash["clube"][key]["vr"], 
					"vv":competicao_hash["clube"][key]["vv"], 
					"er":competicao_hash["clube"][key]["er"], 
					"ev":competicao_hash["clube"][key]["ev"], 
					"dr":competicao_hash["clube"][key]["dr"], 
					"dv":competicao_hash["clube"][key]["dv"], 
					"gmr":competicao_hash["clube"][key]["gmr"], 
					"gmv":competicao_hash["clube"][key]["gmv"], 
					"gsr":competicao_hash["clube"][key]["gsr"], 
					"gsv":competicao_hash["clube"][key]["gsv"], 
					"pr":competicao_hash["clube"][key]["pr"], 
					"pv":competicao_hash["clube"][key]["pv"]
				}
		
		tabela_ordem_keys = sorted(tabela_total, 
		cmp=lambda x,y:self.cmp_liga_classificacao_real(tabela_total[x], tabela_total[y]), 
		reverse=True)

		#vamos adicionar posições
		posicao = 1
		for elem in tabela_ordem_keys:
			tabela_total[elem]["psr"] = posicao
			tabela_ordenada_real["total"].append(tabela_total[elem])
			posicao += 1
		
		tabela_ordem_keys = sorted(tabela_total, 
		cmp=lambda x,y:self.cmp_liga_classificacao_virtual(tabela_total[x], tabela_total[y]), 
		reverse=True)
		
		#agora é construir uma lista com mapas
		posicao = 1
		for elem in tabela_ordem_keys:
			tabela_total[elem]["psv"] = posicao
			tabela_ordenada_virtual["total"].append(tabela_total[elem])
			posicao += 1	
			
		# classificacao PARCIAL			
		for idx, stat_parcial in enumerate(stats_parcial):
			
			tabela_parcial = {}

			for key, value in stat_parcial["clube"].items():

				tabela_parcial[key] = {
				"clu":key,
				"psr":0, "psv":0, 
				"jr":value["jr"],
				"vr":value["vr"], 
				"vv":value["vv"], 
				"er":value["er"], 
				"ev":value["ev"], 
				"dr":value["dr"], 
				"dv":value["dv"], 
				"gmr":value["gmr"], 
				"gmv":value["gmv"], 
				"gsr":value["gsr"], 
				"gsv":value["gsv"], 
				"pr":value["pr"], 
				"pv":value["pv"]
				}
			
			tabela_ordem_keys = sorted(tabela_parcial, 
			cmp=lambda x,y:self.cmp_liga_classificacao_real(tabela_parcial[x], tabela_parcial[y]),
			reverse=True)
			
			tabela_parcial_2 = {"jor_nome":stat_parcial["jornada"].jor_nome, 
									"jor_ordem":stat_parcial["jornada"].jor_ordem,
									"classificacao_parcial":[]}

			#vamos adicionar posições
			posicao = 1
			for elem in tabela_ordem_keys:
				tabela_parcial[elem]["psr"] = posicao
				tabela_parcial_2["classificacao_parcial"].append(tabela_parcial[elem])
				posicao += 1
		
			tabela_ordenada_real["parcial"].append(tabela_parcial_2)
						
			tabela_parcial_2 = {"jor_nome":stat_parcial["jornada"].jor_nome, 
									"jor_ordem":stat_parcial["jornada"].jor_ordem,
									"classificacao_parcial":[]}

			tabela_ordem_keys = sorted(tabela_parcial, 
			cmp=lambda x,y:self.cmp_liga_classificacao_virtual(tabela_parcial[x], tabela_parcial[y]),
			reverse=True)
		
			#agora é construir uma lista com mapas
			posicao = 1
			for elem in tabela_ordem_keys:
				tabela_parcial[elem]["psv"] = posicao
				tabela_parcial_2["classificacao_parcial"].append(tabela_parcial[elem])
				posicao += 1	

			tabela_ordenada_virtual["parcial"].append(tabela_parcial_2)
		
		return tabela_ordenada_real, tabela_ordenada_virtual

	# gera objectos para colocar no namespace "classificacao_real", "classificacao_virtual"
	# no AcumuladorCompeticao
	# 
	# nota: este não gera stats_parcial
	
	
	def gera_classificacao_taca(self, competicao, stats_parcial, competicao_hash):
		
		self.competicao = competicao
		jogos = Jogo.all().filter("jog_competicao = ", self.competicao).fetch(1000)

		for jogo in jogos:
			if jogo.jog_clube1 != None and jogo.jog_clube2 != None:
				if not self.jogos_by_clube1.has_key(jogo.jog_clube1.key().id()):
					self.jogos_by_clube1[jogo.jog_clube1.key().id()] = []
				self.jogos_by_clube1[jogo.jog_clube1.key().id()].append(jogo)
		
		tabela_total_2 = []
		tabela_parcial_2 = []
		
		# vou fazendo a classificacao PARCIAL, e vou preenchendo a TOTAL
		# nota que as parciais já são acumuladores. 
		# a forma que tenho de saber quando o TOTAL tem de parar na PARCIAL 
		# que diz respeito ao último jogo, é ao verificar se há diferenças entre 
		# jogos jogados
		
		jogos_jogados = {}

		tabela_total = {}
		
		 
		for idx, stat_parcial in enumerate(stats_parcial):
			
			tabela_parcial = {}
			
			for key, value in stat_parcial["clube"].items():
				
				tabela_parcial[key] = {
				"clu":key,
				"psr":stat_parcial["jornada"].jor_nome_completo, 
				"psv":stat_parcial["jornada"].jor_nome_completo,
				"jn":stat_parcial["jornada"].jor_nome, 
				"jo":stat_parcial["jornada"].jor_ordem, 
				"jr":value["jr"],
				"ve":value["vr"], 
				"vv":value["vv"], 
				"er":value["er"], 
				"ev":value["ev"], 
				"dr":value["dr"], 
				"dv":value["dv"], 
				"gmr":value["gmr"], 
				"gmv":value["gmv"], 
				"gsr":value["gsr"], 
				"gsv":value["gsv"] 
				}
				
				if not tabela_total.has_key(key):
					
					jogos_jogados[key] = 0
					
					tabela_total[key] = {
					"clu":key,
					"jr":0,
					"vr":0, 
					"vv":0, 
					"er":0, 
					"ev":0, 
					"dr":0, 
					"dv":0, 
					"gmr":0, 
					"gmv":0, 
					"gsr":0, 
					"gsv":0 
				}
				
				# se value["jr"] != jogos_jogados:
				# quer dizer que este PARCIAL possui info com mais jogos do que aquele 
				# que já acumulámos no TOTAL.
				# quando for igual, quer dizer que o PARCIAL já está a andar em jornadas 
				# com jogos que ainda não foram disputados por este clube.

				if value["jr"] != jogos_jogados[key]:
					
					jogos_jogados[key] = value["jr"]
					tabela_total[key]["psr"] = stat_parcial["jornada"].jor_nome_completo
					tabela_total[key]["psv"] = stat_parcial["jornada"].jor_nome_completo
					tabela_total[key]["jn"] = stat_parcial["jornada"].jor_nome 
					tabela_total[key]["jo"] = stat_parcial["jornada"].jor_ordem 
					tabela_total[key]["jr"] = value["jr"]
					tabela_total[key]["vr"] = value["vr"]
					tabela_total[key]["vv"] = value["vv"]
					tabela_total[key]["er"] = value["er"]
					tabela_total[key]["ev"] = value["ev"]
					tabela_total[key]["dr"] = value["dr"]
					tabela_total[key]["dv"] = value["dv"]
					tabela_total[key]["gmr"] = value["gmr"]
					tabela_total[key]["gmv"] = value["gmv"] 
					tabela_total[key]["gsr"] = value["gsr"]
					tabela_total[key]["gsv"] = value["gsv"] 

			# não pode ter reverse, porque quanto maior a ordem, melhor
			tabela_ordem_keys = sorted(tabela_parcial, 
			cmp=lambda x,y:self.cmp_taca_classificacao_real(tabela_parcial[x], tabela_parcial[y]) )
			
			for elem in tabela_ordem_keys:
				tabela_parcial_2.append(tabela_parcial[elem])

		logging.info("total")
		# não pode ter reverse, porque quanto maior a ordem, melhor

		tabela_ordem_keys = sorted(tabela_total, 
		cmp=lambda x,y:self.cmp_taca_classificacao_real(tabela_total[x], tabela_total[y]) )
			
		logging.info(tabela_ordem_keys)	
		for elem in tabela_ordem_keys:
			tabela_total_2.append(tabela_total[elem])
				
		tabela_ordenada_real = {"total":tabela_total_2 , "parcial":tabela_parcial_2 }
		tabela_ordenada_virtual = {"total":tabela_total_2, "parcial":tabela_parcial_2 }

		return tabela_ordenada_real, tabela_ordenada_virtual

