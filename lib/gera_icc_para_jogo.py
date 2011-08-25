# -*- coding: utf-8 -*-

import logging
import re
import config 
from classes import * #Lance

translator_descricao_classe_lance = [
	"--",
	"Factor de resultado final alterado e com pontos redistribuídos",
	"Factor de resultado final alterado mas os pontos ficam na mesma",
	"Factor de golo irregular mas validado",
	"Factor de golo legal mas invalidado",
	"Factor de penalti inexistente assinalado e concretizado", 
	"Factor de penalti inexistente assinalado mas não concretizado", 
	"Factor de penalti existente mas não assinalado", 
	"Factor de fora-de-jogo assinalado indevidamente que é um golo iminente", 
	"Factor de fora-de-jogo assinalado indevidamente que não é situação de golo iminente", 
	"Factor de fora-de-jogo existente, mas não assinalado e que resulta em golo", 
	"Factor de fora-de-jogo existente, mas não assinalado e que não resulta em golo", 
	"Factor de cartão vermelho que ficou por mostrar", 
	"Factor de cartão vermelho mostrado injustamente", 
	"Factor de cartão amarelo que ficou por mostrar", 
	"Factor de cartão amarelo mostrado injustamente", 
	"Factor de falta em zona perigosa assinalada que não existiu, e que resulta em golo",
	"Factor de falta em zona perigosa assinalada que não existiu, e que não resulta em golo",
	"Factor de falta em zona perigosa existente que ficou por assinalar"
]

translator_peso_classe_lance = [0.0, 1.0, 0.5,
1.0, 1.0, 0.9, 0.9, 0.9, 0.75, 0.5, 0.75, 0.75, 0.5, 0.5,
0.4, 0.4, 0.4, 0.3, 0.3]

translator_descricao_risco_jogo = ["Desconhecido","Baixo","Médio","Alto"]
translator_peso_risco_jogo = [0.5, 0.5, 1.0, 1.5]
# jogo entre os 4 primeiros classificados da época passada (1ª volta), ou 1ª volta (2ª volta)
# jogo que inclui um dos 4 primeiros classificados da época passada (1ª volta), ou 1ª volta (2ª volta)
# jogo entre nenhum dos 4 primeiros classificados da época passada (1ª volta), ou 1ª volta (2ª volta)

translator_descricao_tempo_lance = ["[0-15]min","[16-30]min","[31-45]min","[46-60]min","[61-75]min","[76-]min","[?]min",
"[0-15]min*","[16-30]min*","[31-45]min*","[46-60]min*","[61-75]min*","[76-]min*","[?]min*"]
translator_peso_tempo_lance = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.0,
										1.4, 1.2, 1.0, 0.8, 0.6, 0.4, 1.0 ]

def gera_descricao_e_peso_tempo_lance(minuto, classe):
	descricao = 0
	peso = 0
	
	if re.search(r'([Aa]marelo|[Vv]ermelho)', Lance.translation_classe[classe]) is not None: 
		if not minuto: 
			descricao = translator_descricao_tempo_lance.index("[?]min*")
			return descricao, translator_peso_tempo_lance[descricao]
		if minuto < 16:
			descricao = translator_descricao_tempo_lance.index("[0-15]min*")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 31:
			descricao = translator_descricao_tempo_lance.index("[16-30]min*")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 46:
			descricao = translator_descricao_tempo_lance.index("[31-45]min*")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 61:
			descricao = translator_descricao_tempo_lance.index("[46-60]min*")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 76:
			descricao = translator_descricao_tempo_lance.index("[61-75]min*")
			return descricao, translator_peso_tempo_lance[descricao]
		else:
			descricao = translator_descricao_tempo_lance.index("[76-]min*")
			return descricao, translator_peso_tempo_lance[descricao]
	else:
		if not minuto: 
			descricao = translator_descricao_tempo_lance.index("[?]min")
			return descricao, translator_peso_tempo_lance[descricao]
		if minuto < 16:
			descricao = translator_descricao_tempo_lance.index("[0-15]min")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 31:
			descricao = translator_descricao_tempo_lance.index("[16-30]min")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 46:
			descricao = translator_descricao_tempo_lance.index("[31-45]min")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 61:
			descricao = translator_descricao_tempo_lance.index("[46-60]min")
			return descricao, translator_peso_tempo_lance[descricao]
		elif minuto < 76:
			descricao = translator_descricao_tempo_lance.index("[61-75]min")
			return descricao, translator_peso_tempo_lance[descricao]
		else:
			descricao = translator_descricao_tempo_lance.index("[76-]min")
			return descricao, translator_peso_tempo_lance[descricao]

def pontosClube1(golos1, golos2):
	if golos1 > golos2:
		return 3 
	if golos1 == golos2:
		return 1 
	return 0
	
def pontosClube2(golos1, golos2):
	if golos1 < golos2:
		return 3 
	if golos1 == golos2:
		return 1 
	return 0

# calcula o resultado de um jogo até ao minuto x
def calcular_resultado_parcial(jogo, minuto_limite):
	res1 = 0
	res2 = 0
	if  minuto_limite: 
		for jjj in jogo.jog_jogadores:
			if jjj.jjj_golos_minutos and jjj.jjj_golos_minutos != []:
				for minuto_index, val in enumerate(jjj.jjj_golos_minutos):
					if jjj.jjj_golos_minutos[minuto_index] < minuto_limite:
						# ok, vamos a ver por quem marcou
						if jjj.jjj_clube.clu_nome == jogo.jog_clube1.clu_nome:
							# vamos lá a ver se não é autogolo
							if len(jjj.jjj_golos_tipos) > minuto_index and  jjj.jjj_golos_tipos[minuto_index] != "p.b.":
								res1 += 1
							else:
								res2 += 1
						else:
							if len(jjj.jjj_golos_tipos) > minuto_index and jjj.jjj_golos_tipos[minuto_index] != "p.b.":
								res2 += 1
							else:
								res1 += 1
	return res1, res2

def gera_descricao_e_peso_resultado_parcial(jogo, minuto_limite, 
	golos_virt_delta_1, golos_virt_delta_2):

	golos_orig_1, golos_orig_2 = calcular_resultado_parcial(jogo, minuto_limite)

	golos_virt_1 = golos_orig_1 + golos_virt_delta_1
	golos_virt_2 = golos_orig_2 + golos_virt_delta_2

	p_orig_1 = pontosClube1(golos_orig_1, golos_orig_2)
	p_virt_1 = pontosClube1(golos_virt_1, golos_virt_2)
	
	resultados = str(golos_orig_1)+"-"+str(golos_orig_2)+" &rarr; "+str(golos_virt_1)+"-"+str(golos_virt_2)
	
	# há mudança entre V, E ou D
	if p_orig_1 != p_virt_1:
		
		return resultados+"<BR>&Delta;: " + str(p_orig_1 - p_virt_1)+ " pontos", 1.3
	
	# mantém-se o V, E ou D
	else:
		diff_original = (golos_orig_1 - golos_orig_2)
		diff_virtual = (golos_virt_1 - golos_virt_2)
		
		# resultado mantém-se:
		if abs(diff_original - diff_virtual) == 0:
			return resultados+"<BR>&Delta;: 0 golos", 1.0, 
		else:
			# há uma diferença de 1 golo
			diff = abs(diff_original - diff_virtual)
			# o delta é de 2->1 ou 1->2
			if diff_original == 1 or diff_virtual == 1:
				return resultados+"<BR>&Delta;: 1 golo", 0.8, 
			else:
				if diff_original == 2 or diff_virtual == 3:
					return resultados+"<BR>&Delta;: 2 golos", 0.6
				else:
					return resultados+"<BR>&Delta;: 3+ golos", 0.4
	

# calcula o risco do jogo
def gera_descricao_e_peso_risco_jogo(jogo):
	# o risco é sempre calculado pelas posições no campeonato. 
	epoca = jogo.jog_jornada.jor_competicao.cmp_epoca
	competicao = epoca.epo_competicoes.filter("cmp_tipo = ", "Liga").get()
	cjc_clubes_da_competicao = ClubeJogaCompeticao.all().filter("cjc_competicao = ", competicao)
	
	descricao = translator_descricao_risco_jogo.index("Desconhecido")
	peso = translator_peso_risco_jogo[descricao]
	
	rank_clube1 = 0
	rank_clube2 = 0
	
	for cjc in cjc_clubes_da_competicao:
		if cjc.cjc_clube == jogo.jog_clube1:
			rank_clube1 = cjc.cjc_classificacao_anterior
		if cjc.cjc_clube == jogo.jog_clube2:
			rank_clube2 = cjc.cjc_classificacao_anterior
	
	if rank_clube1 == 0 or rank_clube1 > 4: 
		if rank_clube2 == 0 or rank_clube2 > 4:
			descricao = translator_descricao_risco_jogo.index("Baixo")
			peso = translator_peso_risco_jogo[descricao]
		else:
			descricao = translator_descricao_risco_jogo.index("Médio")
			peso = translator_peso_risco_jogo[descricao]
	
	else:
		if rank_clube2 == 0 or rank_clube2 > 4:
			descricao = translator_descricao_risco_jogo.index("Médio")
			peso = translator_peso_risco_jogo[descricao]
		else:
			descricao = translator_descricao_risco_jogo.index("Alto")
			peso = translator_peso_risco_jogo[descricao]
	
	return descricao, peso 

def calcula_ica_lance(peso_resultado_parcial, peso_tempo, peso_risco, peso_lance_classe):
	return peso_resultado_parcial*peso_tempo*peso_risco*peso_lance_classe

def calcula_ica_agravamento(peso_agravamento, peso_risco):
	return peso_agravamento*peso_risco

def casa_prejudicada_visitante_beneficiado(ica, stats, lance_hash):

	icc_clube1 = -1 * ica
	icc_clube2 = ica

	stats['icc_clube1'] += icc_clube1
	stats['icc_clube2'] += icc_clube2
						
	lance_hash.update({
	  "icc1": icc_clube1, "icc2": icc_clube2, "ica":-1*ica
	})

def casa_beneficiada_visitante_prejudicado(ica, stats, lance_hash):
	
	icc_clube1 = ica
	icc_clube2 = -1 * ica

	stats['icc_clube1'] += icc_clube1
	stats['icc_clube2'] += icc_clube2
						
	lance_hash.update({
		 "icc1": icc_clube1, "icc2": icc_clube2, "ica":-1*ica
	})
	
def analisa(jogo):
		
	stats = {
		 "clube1":jogo.jog_clube1.key().id(), 
		 "clube2":jogo.jog_clube2.key().id(),
		 "icc_clube1":0.0, "icc_clube2":0.0, 
		  # icc_golos serve para contabilizar quem foi prejudicado, quem foi beneficiado em questão de pontos
		 "icc_golos1":0, "icc_golos2":0,
		 "ica":0.0, # indice de cegueira do árbitro. Positivo = boa arbitragem. Negativo = má arbitragem.
		 "ia":None, # influência do árbitro
		 "julgamento_arbitro":None, #pendor do árbitro, prejudicou / beneficiou quem
		 "go1":jogo.jog_golos_clube1, #golos_originais_equipa_casa
		 "go2":jogo.jog_golos_clube2, #golos_originais_equipa_visitante
		 "gv1":jogo.jog_golos_clube1, #golos_virtuais_equipa_casa
		 "gv2":jogo.jog_golos_clube2,#golos_virtuais_equipa_visitante
		
		 "po1":pontosClube1(jogo.jog_golos_clube1, jogo.jog_golos_clube2),
		 "po2":pontosClube2(jogo.jog_golos_clube1, jogo.jog_golos_clube2),
		 "pv1":pontosClube1(jogo.jog_golos_clube1, jogo.jog_golos_clube2),
		 "pv2":pontosClube2(jogo.jog_golos_clube1, jogo.jog_golos_clube2),
		
		 "lances":[],# para cada lance.key().id()
		 "bonus":None # bonus para o geral dos lances
	}
		
	if jogo.jog_arbitro:
		stats["arb"] = jogo.jog_arbitro.key().id()
		
	# calcular o risco do jogo
	descricao_risco_jogo, peso_risco_jogo = gera_descricao_e_peso_risco_jogo(jogo)
		
	# isto é tudo para situações em que o árbitro está errado		
	for lance in jogo.jog_lances.order("lan_numero"):
			
		lance_hash = {"lan":lance.key().id(),
			"num":lance.lan_numero,
			"min":lance.lan_minuto,
			 "clu1":jogo.jog_clube1.key().id(), 
			 "clu2":jogo.jog_clube2.key().id(),
			 "tip":lance.lan_classe,
			 "icc1": 0.0, "icc2": 0.0, "ica":0.0
		}
			
		# calcular a decisão com base nos comentadores
		# as decisões são quatro números: 
		# 1 - o árbitro esteve bem
		# 2 - o árbitro beneficiou a equipa da casa
		# 3 - o árbitro beneficiou a equipa visitante
		# 4 - dá-se o benefício do árbitro (tem o mesmo efeito que 0)

		decisao = lance.decide_lance()
		lance_hash["dn"] = decisao # adiciona a decisão à hash
		
		descricao_tempo_lance, peso_tempo_lance = gera_descricao_e_peso_tempo_lance(lance.lan_minuto, lance.lan_classe)

		lance_hash["d_tmp"] = descricao_tempo_lance
		lance_hash["p_tmp"] = peso_tempo_lance

		lance_hash["d_ris"] = descricao_risco_jogo
		lance_hash["p_ris"] = peso_risco_jogo
		
		peso_classe_lance = None
		descricao_classe_lance = None
		
		if lance.lan_classe == Lance.translation_classe.index('Amarelo mostrado a jogador da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Amarelo mostrado a jogador da equipa visitante'):
			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de cartão amarelo mostrado injustamente")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Vermelho mostrado a jogador da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Vermelho mostrado a jogador da equipa visitante'):
			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de cartão vermelho mostrado injustamente")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Amarelo não mostrado a jogador da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Amarelo não mostrado a jogador da equipa visitante'):
			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de cartão amarelo que ficou por mostrar")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Vermelho não mostrado a jogador da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Vermelho não mostrado a jogador da equipa visitante'):
					
			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de cartão vermelho que ficou por mostrar")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e convertida, no ataque da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e convertida, no ataque da equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de falta em zona perigosa assinalada que não existiu, e que resulta em golo")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]
			
		elif lance.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e não convertida, no ataque da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e não convertida, no ataque da equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de falta em zona perigosa assinalada que não existiu, e que não resulta em golo")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]
			
		elif lance.lan_classe == Lance.translation_classe.index('Falta perigosa não assinalada, no ataque da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Falta perigosa não assinalada, no ataque da equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de falta em zona perigosa existente que ficou por assinalar")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa da casa, de golo fácil') or \
			lance.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa visitante, de golo fácil'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de fora-de-jogo assinalado indevidamente que é um golo iminente")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa da casa, de golo difícil') or \
			lance.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa visitante, de golo difícil'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de fora-de-jogo assinalado indevidamente que não é situação de golo iminente")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa da casa, que resultou em golo') or \
			lance.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa visitante, que resultou em golo'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de fora-de-jogo existente, mas não assinalado e que resulta em golo")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa da casa, que não resultou em golo') or \
			lance.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa visitante, que não resultou em golo'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de fora-de-jogo existente, mas não assinalado e que não resulta em golo")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Penalti assinalado e convertido a atacante da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Penalti assinalado e convertido a atacante da equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de penalti inexistente assinalado e concretizado")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Penalti assinalado e não convertido a atacante da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Penalti assinalado e não convertido a atacante da equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de penalti inexistente assinalado mas não concretizado")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Penalti não assinalado a atacante da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Penalti não assinalado a atacante da equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de penalti existente mas não assinalado")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Golo marcado e validado para a equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Golo marcado e validado para a equipa visitante'):

			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de golo irregular mas validado")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		elif lance.lan_classe == Lance.translation_classe.index('Golo marcado mas invalidado para a equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index('Golo marcado mas invalidado para a equipa visitante'):
			descricao_classe_lance = translator_descricao_classe_lance.index("Factor de golo legal mas invalidado")
			peso_classe_lance = translator_peso_classe_lance[descricao_classe_lance]

		lance_hash["d_cla"] = descricao_classe_lance
		lance_hash["p_cla"] = peso_classe_lance

		# calcular compensações de golos, ou golos virtuais
				
		golos_virtuais_parciais1 = 0
		golos_virtuais_parciais2 = 0
		
		# situações onde golos virtuais tenho de retirar um À equipa da casa
		if lance.lan_classe == Lance.translation_classe.index(
			 'Falta perigosa assinalada e convertida, no ataque da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index(
			 'Fora de jogo não assinalado no ataque da equipa da casa, que resultou em golo') or \
			lance.lan_classe == Lance.translation_classe.index(
			 'Penalti assinalado e convertido a atacante da equipa da casa') or \
			lance.lan_classe == Lance.translation_classe.index(
			 'Golo marcado e validado para a equipa da casa'):
			
			if decisao == Lance.translation_julgamento_arbitro.index('Beneficiou a equipa da casa'): 

				stats['gv1'] -= 1
				stats['icc_golos1'] += 1

				lance_hash.update({"icc1_g": -1})

		# situações onde golos virtuais tenho de adicionar um à equipa visitante	
		elif lance.lan_classe == Lance.translation_classe.index(
			 'Fora de jogo assinalado no ataque da equipa visitante, de golo fácil') or \
			  lance.lan_classe == Lance.translation_classe.index(
			 'Penalti não assinalado a atacante da equipa visitante') or \
			  lance.lan_classe == Lance.translation_classe.index(
			 'Golo marcado mas invalidado para a equipa visitante'):

			if decisao == Lance.translation_julgamento_arbitro.index('Beneficiou a equipa da casa'): 

				stats['gv2'] += 1	
				stats['icc_golos2'] -= 1

				lance_hash.update({"icc2_g":1})

		# situações onde golos virtuais tenho de retirar um à equipa visitante	
		elif lance.lan_classe == Lance.translation_classe.index(
			 'Falta perigosa assinalada e convertida, no ataque da equipa visitante') or \
			lance.lan_classe == Lance.translation_classe.index(
			 'Fora de jogo não assinalado no ataque da equipa visitante, que resultou em golo') or \
			lance.lan_classe == Lance.translation_classe.index(
			 'Penalti assinalado e convertido a atacante da equipa visitante') or \
			lance.lan_classe == Lance.translation_classe.index(
			 'Golo marcado e validado para a equipa visitante'):

			if decisao == Lance.translation_julgamento_arbitro.index('Beneficiou a equipa visitante'): 

				stats['gv2'] -= 1
				stats['icc_golos2'] += 1

				lance_hash.update({"icc2_g": -1})			
				
		# situações onde golos virtuais tenho de adicionar um à equipa da casa	
		elif lance.lan_classe == Lance.translation_classe.index(
			 'Fora de jogo assinalado no ataque da equipa da casa, de golo fácil') or \
			  lance.lan_classe == Lance.translation_classe.index(
			 'Penalti não assinalado a atacante da equipa da casa') or \
			  lance.lan_classe == Lance.translation_classe.index(
			 'Golo marcado mas invalidado para a equipa da casa'):

			if decisao == Lance.translation_julgamento_arbitro.index('Beneficiou a equipa visitante'): 

				stats['gv1'] += 1	
				stats['icc_golos1'] -= 1
						
				lance_hash.update({"icc1_g": 1})

		# usar os golos virtuais para calcular peso de resultado parcial

		if lance_hash.has_key("icc1_g"):
			golos_virtuais_parciais1 = lance_hash["icc1_g"]
		if lance_hash.has_key("icc2_g"):
			golos_virtuais_parciais2 = lance_hash["icc2_g"]

		descricao_resultado_parcial, peso_resultado_parcial = gera_descricao_e_peso_resultado_parcial(
			jogo, lance.lan_minuto, golos_virtuais_parciais1, golos_virtuais_parciais2)
		
		lance_hash["d_res"] = descricao_resultado_parcial
		lance_hash["p_res"] = peso_resultado_parcial

######################
# arbitro esteve bem #
######################

		ica = calcula_ica_lance(peso_resultado_parcial, peso_tempo_lance, peso_risco_jogo, peso_classe_lance)

		if decisao == Lance.translation_julgamento_arbitro.index('Sem benefícios'):

			stats['ica'] += ica
			lance_hash.update({"icc1": 0.0, "icc2": 0.0, "ica":ica})

######################
# arbitro esteve mal #
######################
				
		else:
			stats['ica'] += -1 * ica

			if decisao == Lance.translation_julgamento_arbitro.index('Beneficiou a equipa visitante'): 
						
				casa_prejudicada_visitante_beneficiado(ica, stats, lance_hash)

			if decisao == Lance.translation_julgamento_arbitro.index('Beneficiou a equipa da casa'): 

				casa_beneficiada_visitante_prejudicado(ica, stats, lance_hash)

			# at last, add lance to list
		stats['lances'].append(lance_hash)
	
######################		
###### BONUS #########
######################

	descricao_pontos_redistribuidos = translator_descricao_classe_lance.index("Factor de resultado final alterado e com pontos redistribuídos")
	peso_pontos_redistribuidos = translator_peso_classe_lance[descricao_pontos_redistribuidos]

	descricao_pontos_na_mesma = translator_descricao_classe_lance.index("Factor de resultado final alterado mas os pontos ficam na mesma")	
	peso_pontos_na_mesma = translator_peso_classe_lance[descricao_pontos_na_mesma]

	resultado_virtual = u"%s-%s" % (stats['gv1'], stats['gv2'])
	
	# Quando há roubalheira (ou seja, golos mudam...)
	if stats['gv1'] != stats['go1'] or stats['go2'] != stats['gv2']:

		# vitória original da equipa da casa:
		if stats['go1'] > stats['go2']:

			stats["pv1"] = pontosClube1(stats["gv1"], stats["gv2"])
			stats["pv2"] = pontosClube2(stats["gv1"], stats["gv2"])
					
			# se se mantém a vitória da equipa da casa
			if stats['gv1'] > stats['gv2']:
					
				stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado mas não nos pontos.")
				
				# mas por uma diferença maior:
				if (stats['go1'] - stats['go2']) < (stats['gv1'] - stats['gv2']):
						
					# equipa da casa foi beneficiada
					if stats['icc_golos1'] > stats['icc_golos2']:
							
						ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
						stats['icc_clube1'] += ica
						stats['icc_clube2'] -= ica
						stats['ica'] -= ica

						stats['bonus'] = {
							"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
							"rv":resultado_virtual,
							"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
							"icc1": ica, "icc2": -1 * ica, "ica": -1 * ica,
							"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
						  	"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

					# equipa da casa foi prejudicada
					else: 

						ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
						stats['icc_clube1'] -= ica
						stats['icc_clube2'] += ica
						stats['ica'] -= ica

						stats['bonus'] = {
							"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
							"rv":resultado_virtual,
							"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
							"icc1": -1 * ica, "icc2": ica, "ica": -1 * ica,
							"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
						  	"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

				# mas por uma diferença  menor: 
				elif (stats['go1'] - stats['go2']) > (stats['gv1'] - stats['gv2']):
						
					# equipa da casa foi beneficiada
					if stats['icc_golos1'] > stats['icc_golos2']:
							
						ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
						stats['icc_clube1'] += ica
						stats['icc_clube2'] -= ica
						stats['ica'] -= ica

						stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": ica, "icc2": -1 * ica, "ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

					# equipa da casa foi prejudicada
					else:
							ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
							stats['icc_clube1'] -= ica
							stats['icc_clube2'] += ica
							stats['ica'] -= ica
							
							stats['bonus'] = { 
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": -1 * ica, "icc2": ica, "ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

			# passou de vitória a um empate ou uma derrota - quem foi beneficiado?
			else:
				stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado e nos pontos.")
					
				# equipa da casa foi beneficiada
				if stats['icc_golos1'] > stats['icc_golos2']:
													
						ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
						stats['icc_clube1'] += ica
						stats['icc_clube2'] -= ica
						stats['ica'] -= ica

						stats['bonus'] = {
							"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
							"rv":resultado_virtual,
							"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
							"icc1": ica,"icc2": -1 * ica,	"ica": -1 * ica,
							"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
							"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

				else:
						ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
						stats['icc_clube1'] -= ica
						stats['icc_clube2'] += ica
						stats['ica'] -= ica
							
						stats['bonus'] = {
							"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
							"rv":resultado_virtual,
							"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
							"icc1": -1 * ica,	"icc2": ica,	"ica": -1 * ica,
							"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
							"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}
			
		# derrota original da equipa da casa:
		elif stats['go1'] < stats['go2']:

			stats["pv1"] = pontosClube1(stats["gv1"], stats["gv2"])
			stats["pv2"] = pontosClube2(stats["gv1"], stats["gv2"])

			# se se mantém a derrota da equipa da casa
			if stats['gv1'] < stats['gv2']:

				stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado mas não nos pontos.")
					
				# mas por uma diferença maior: 
				if (stats['go2'] - stats['go1'] ) < (stats['gv2'] - stats['gv1']):
						
						# equipa da casa beneficiada
						
						if stats['icc_golos1'] > stats['icc_golos2']:
						
							ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
							stats['icc_clube1'] += ica
							stats['icc_clube2'] -= ica
							stats['ica'] -= ica

							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": ica,"icc2": -1 * ica,	"ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

						else:
							ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
							stats['icc_clube1'] -= ica
							stats['icc_clube2'] += ica
							stats['ica'] -= ica
							
							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": -1 * ica, "icc2": ica, "ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

				# mas por uma diferença menor: 
				elif (stats['go2'] - stats['go1'] ) > (stats['gv2'] - stats['gv1']):

						if stats['icc_golos1'] > stats['icc_golos2']:
						
						# equipa da casa beneficada 
							ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
							stats['icc_clube1'] += ica
							stats['icc_clube2'] -= ica
							stats['ica'] -= ica

							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": ica,"icc2": -1 * ica,"ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

						# equipa da casa prejudicada
						else:
							ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
							stats['icc_clube1'] -= ica
							stats['icc_clube2'] += ica
							stats['ica'] -= ica

							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
								"rv":resultado_virtual,
 								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": -1 * ica, "icc2": ica, "ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

			# passou de derrota a um empate ou uma vitória - a equipa da casa é que é beneficiada:
			else:
					
				stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado e nos pontos.")
					
				# equipa da casa foi (?) beneficiada
				if stats['icc_golos1'] > stats['icc_golos2']:
						
							ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
							stats['icc_clube1'] += ica
							stats['icc_clube2'] -= ica
							stats['ica'] -= ica

							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
								"rv":resultado_virtual,
 								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": ica,"icc2": -1 * ica,"ica": -1 * ica,
								"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}
							
				# equipa da casa foi prejudicada
				else:
							ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
							stats['icc_clube1'] -= ica
							stats['icc_clube2'] += ica
							stats['ica'] -= ica
							
							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": -1 * ica, "icc2": ica,	"ica": -1 * ica,
								"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}
							
		# empate original
		elif stats['go1'] == stats['go2']:
			stats['ia']  = 1
				
			stats["pv1"] = pontosClube1(stats["gv1"], stats["gv2"])
			stats["pv2"] = pontosClube2(stats["gv1"], stats["gv2"])
					
			# se se converte numa vitória da equipa da casa: 
			if stats['gv1'] > stats['gv2']:
				stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado e nos pontos.")
					
				# equipa da casa foi beneficiada.
				if stats['icc_golos1'] > stats['icc_golos2']:
					
							ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
							stats['icc_clube1'] += ica
							stats['icc_clube2'] -= ica
							stats['ica'] -= ica

							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": ica,"icc2": -1 * ica, "ica": -1 * ica,
								"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

				# equipa da casa foi prejudicada
				else: 
							ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
							stats['icc_clube1'] -= ica
							stats['icc_clube2'] += ica
							stats['ica'] -= ica
							
							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": -1 * ica,	"icc2": ica,"ica": -1 * ica,
								"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}
						
			# se se converte numa derrota da equipa da casa	
			elif stats['gv1'] < stats['gv2']:
				stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado e nos pontos.")

				# equipa da casa foi beneficiada
				if stats['icc_golos1'] > stats['icc_golos2']:
						
							ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
							stats['icc_clube1'] += ica
							stats['icc_clube2'] -= ica
							stats['ica'] -= ica

							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": ica,"icc2": -1 * ica,"ica": -1 * ica,
								"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

	
				# equipa da casa foi prejudicada
				else:
							ica = calcula_ica_agravamento(peso_pontos_redistribuidos, peso_risco_jogo)
							stats['icc_clube1'] -= ica
							stats['icc_clube2'] += ica
							stats['ica'] -= ica
							
							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante"),
								"rv":resultado_virtual,
								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": -1 * ica,	"icc2": ica,"ica": -1 * ica,
								"d_agr":descricao_pontos_redistribuidos, "p_agr": peso_pontos_redistribuidos, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

			# se se converte noutro empate, com golos diferentes
			# teoricamente, ambas as equipas nem ficam beneficiadas nem ficam prejudicadas 
			# vamos meter peso a 0, senão os ICC não ficam simétricos, e assim não tenho de 
			# escolher se ambos ficam beneficiados ou prejudicados. 
			elif stats['gv1'] == stats['gv2']:
				if stats['gv1'] != stats['go1']:
							stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro teve influência no resultado mas não nos pontos.")
						
							ica = calcula_ica_agravamento(peso_pontos_na_mesma, peso_risco_jogo)
							stats['icc_clube1'] += 0
							stats['icc_clube2'] += 0
							stats['ica'] -= ica
							
							stats['bonus'] = {
								"dn":Jogo.translation_julgamento_arbitro.index("Sem benefícios"),
								"rv":resultado_virtual,
 								"clu1":jogo.jog_clube1.key().id(), "clu2":jogo.jog_clube2.key().id(),
								"icc1": 0,"icc2": 0,"ica": -1 * ica,
								"d_agr":descricao_pontos_na_mesma, "p_agr": peso_pontos_na_mesma, 
								"d_ris": descricao_risco_jogo, "p_ris": peso_risco_jogo}

	########################################	
	# vamos preencher, no final do jogo,   #
	# a influência e julgamento do árbitro #
	########################################
	
	# se não há lances: não sei
	if stats['lances'] == []:
		stats['julgamento_arbitro']= Jogo.translation_julgamento_arbitro.index("Sem informação")
		stats['ia']= Jogo.translation_influencia_arbitro.index("Sem informação.")
	
	# se há lances: 
	else:
		
		########### JA ###########
		
		# benefício casa
		if stats['icc_clube1'] > stats['icc_clube2']:
			stats['julgamento_arbitro'] = Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa da casa")
		# benefício visitante
		elif stats['icc_clube1'] < stats['icc_clube2']:
			stats['julgamento_arbitro'] = Jogo.translation_julgamento_arbitro.index("Beneficiou a equipa visitante")
		# benefício nenhum
		else:
			stats['julgamento_arbitro'] = Jogo.translation_julgamento_arbitro.index("Sem benefícios")

		############# IA ##########

		# se o stats['ia'] é None, é porque não houve bonus que mexeram no valor, e é porque 
		# houve lances. Ou seja, o árbitro não influenciou.
		
		if stats['ia'] == None:
			  stats['ia'] = Jogo.translation_influencia_arbitro.index("O árbitro não teve influência no resultado.")

	return stats
