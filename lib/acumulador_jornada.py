# -*- coding: utf-8 -*-

from google.appengine.api import memcache

import logging
import re
import config 
import datetime
import collections 

import acumulador

from classes import * #Lance

import gera_icc_para_jogo

def gera(jornada):
	
	stats = {
		"arbitro": {},
		"clube": {},
		"jogo": {},
		"jogador": {},
		"lance": {},
		"bonus": {}
	}
	
	for jogo in jornada.jor_jogos:

		gera_estatistica_para_jogo(jogo, stats)
		jog_id = jogo.key().id()
		
		# vamos escrever stats importantes na BD do Jogo e Lance
		if stats["jogo"].has_key(jog_id):
			jogo.jog_icc = abs(stats["jogo"][jog_id]["icc1"])

			jogo.jog_ica = stats["jogo"][jog_id]["ica"]
			jogo.jog_influencia_arbitro = stats["jogo"][jog_id]["ia"]
			jogo.jog_julgamento_arbitro = stats["jogo"][jog_id]["ja"]

			jogo.jog_golos_virtuais_clube1 =  stats["jogo"][jog_id]["gv1"]
			jogo.jog_golos_virtuais_clube2 =  stats["jogo"][jog_id]["gv2"]

			if stats["jogo"][jog_id]["ja"] == \
				Jogo.translation_julgamento_arbitro.index('Beneficiou a equipa da casa'):
				jogo.jog_clube_beneficiado = jogo.jog_clube2.key()
				jogo.jog_clube_prejudicado = jogo.jog_clube1.key()
			elif stats["jogo"][jog_id]["ja"] == \
				Jogo.translation_julgamento_arbitro.index('Beneficiou a equipa visitante'):
				jogo.jog_clube_beneficiado = jogo.jog_clube1.key()
				jogo.jog_clube_prejudicado = jogo.jog_clube2.key()
			
		jogo.jog_clubes = [jogo.jog_clube1.key(),jogo.jog_clube2.key()]
		jogo.put()
#		logging.info(jogo.key().id())
#		logging.info(jogo.jog_icc)	
		
		for lance in jogo.jog_lances:
			lan_id = lance.key().id()
			lance.lan_icc = abs(stats["lance"][lan_id]["icc1"])
			lance.lan_ica = stats["lance"][lan_id]["ica"]
			lance.lan_clubes = [jogo.jog_clube1.key(),jogo.jog_clube2.key()]
			
			lan_causa, lan_apitado, lan_consequencia = lance.divide_tipo_lance() 
			lance.lan_causa = lan_causa
			lance.lan_apitado = lan_apitado
			lance.lan_consequencia = lan_consequencia
			lance.lan_julgamento_arbitro = stats["lance"][lan_id]["dn"]
			
			if stats["lance"][lan_id]["dn"] == \
				Lance.translation_julgamento_arbitro.index('Beneficiou a equipa da casa'):
	
				lance.lan_clube_beneficiado = jogo.jog_clube1.key()
				lance.lan_clube_prejudicado = jogo.jog_clube2.key()
				
			elif stats["lance"][lan_id]["dn"] == \
				Lance.translation_julgamento_arbitro.index('Beneficiou a equipa visitante'):
				
				lance.lan_clube_beneficiado = jogo.jog_clube2.key()
				lance.lan_clube_prejudicado = jogo.jog_clube1.key()
			lance.lan_clubes = [jogo.jog_clube1.key(),jogo.jog_clube2.key()]
			lance.put()
			
	return stats
	
def gera_estatistica_para_jogo(jogo, stats):

	# É AQUI que decido quais os parâmetros, calculados no gera_icc_jogo, que passam para os acumuladores!
	stat_jogo = {
		"clu1":None,
		"clu2":None,
		"gm":0, # golos marcados
		"icc1":0.0, #icc1
		"icc2":0.0, #icc2
		"ica":0.0, # ica
		"ia":None, # ia
		"ja":None, #julgamento árbitro
		"arb":None, #árbitro_id
		
		"ca":0, # cartoes amarelos
		"cda":0, # cartoes duplo amarelos
		"cv":0, # cartoes vermelhos
		
		"go1":0, #golos_originais_equipa_casa
		"go2":0, #golos_originais_equipa_visitante
		"gv1":0, #golos_virtuais_equipa_casa
		"gv2":0,#golos_virtuais_equipa_visitante
		
		"po1":0, #pontos_originais_equipa_casa
		"po2":0,  #pontos_originais_equipa_visitante
		"pv1":0,#pontos_virtuais_equipa_casa
		"pv2":0#pontos_virtuais_equipa_visitante
	}
	
	stat_clube1 = {
		"jr":0, # jogos realizados
		"vr":0, #vitorias_reais
		"er":0, # empates reais
		"dr":0, #derrotas reais
		"gmr":0, #golos marcados reais
		"gsr":0, # golos sofridos reaos
		"pr":0, #pontos reais
		"vv":0, #vitorias virtuais
		"ev":0, #empates virtuais
		"dv":0, #derrotas virtuais
		"gmv":0, #golos marcados virtuais
		"gsv":0, #golos sofridos virtuais
		"pv":0, #pontos virtuais

		"ca":0, #cartoes amarelos
		"cda":0, #cartoes duplo amarelos
		"cv":0, #cartoes vermelhos

		"a_j":{}, #aarbitro_jogos
		"a_i":{}, #arbitro_icc
		"a_a":{}, #arbitro_amarelos
		"a_da":{}, #arbitro_damarelos
		"a_v":{}, #arbitro_vermelhos

		"j_g":{}, #jogador_golos
		"j_m":{}, #jogador_minutos
		"j_a":{}, #jogador_amarelos
		"j_da":{}, #jogador_damarelos
		"j_v":{} #jogador_vermelhos
	}
	stat_clube2 = {
		"jr":0, # jogos realizados
		"vr":0, #vitorias_reais
		"er":0, # empates reais
		"dr":0, #derrotas reais
		"gmr":0, #golos marcados reais
		"gsr":0, # golos sofridos reaos
		"pr":0, #pontos reais
		"vv":0, #vitorias virtuais
		"ev":0, #empates virtuais
		"dv":0, #derrotas virtuais
		"gmv":0, #golos marcados virtuais
		"gsv":0, #golos sofridos virtuais
		"pv":0, #pontos virtuais

		"ca":0, #cartoes amarelos
		"cda":0, #cartoes duplo amarelos
		"cv":0, #cartoes vermelhos

		"a_j":{}, #aarbitro_jogos
		"a_i":{}, #arbitro_icc
		"a_a":{}, #arbitro_amarelos
		"a_da":{}, #arbitro_damarelos
		"a_v":{}, #arbitro_vermelhos

		"j_g":{}, #jogador_golos
		"j_m":{}, #jogador_minutos
		"j_a":{}, #jogador_amarelos
		"j_da":{}, #jogador_damarelos
		"j_v":{} #jogador_vermelhos
	}
	stat_arbitro = {
		"jr":0, #jogos_realizados
		"ca":0, #cartoes amarelos
		"cda":0, #cartoes duploamarelos
		"cv":0, #cartoes vermelhos

		"rnk":0, #ranking_tabela_icc
		"ica":0, #ica
		
		"j_a":{}, #jogadores_amarelos
		"j_da":{}, #jogadores_duploamarelos
		"j_v":{}, #jogador_vermelhos

		"c_j":{}, #clubes_jogos
		"c_i":{}, #clubes_icc
		"c_a":{}, #clubes_amarelos
		"c_da":{}, #clubes_duploamarelos
		"c_v":{} #clube_vermelhos
	}

	clube1_id = None
	clube2_id = None
	
	if jogo.jog_clube1:
		clube1_id = jogo.jog_clube1.key().id()
		stat_jogo["clu1"] = clube1_id
	if jogo.jog_clube2:
		clube2_id = jogo.jog_clube2.key().id()
		stat_jogo["clu2"] = clube2_id

	arb_id = None

	if jogo.jog_golos_clube1 != None and jogo.jog_golos_clube2 != None:

		###################
		# GERAR ICC STATS #
		###################
		estatisticas_jogo = gera_icc_para_jogo.analisa(jogo)
		
		if estatisticas_jogo.has_key("arb"):
			arb_id = estatisticas_jogo["arb"]
			stat_jogo['arb'] = arb_id

#		logging.info("estatisticas_jogo")
#		logging.info(estatisticas_jogo)
		stat_jogo['icc1'] = estatisticas_jogo["icc_clube1"]
		stat_jogo['icc2'] = estatisticas_jogo["icc_clube2"]
		stat_jogo['ica'] = estatisticas_jogo["ica"]
		stat_jogo['ia'] = estatisticas_jogo["ia"]
		stat_jogo["ja"] = estatisticas_jogo["julgamento_arbitro"]

		stat_jogo['go1'] = estatisticas_jogo["go1"]
		stat_jogo['go2'] = estatisticas_jogo["go2"]
		stat_jogo['gv1'] = estatisticas_jogo["gv1"]
		stat_jogo['gv2'] = estatisticas_jogo["gv2"]
		stat_jogo['po1'] = estatisticas_jogo["po1"]
		stat_jogo['po2'] = estatisticas_jogo["po2"]
		stat_jogo['pv1'] = estatisticas_jogo["pv1"]
		stat_jogo['pv2'] = estatisticas_jogo["pv2"]

		if arb_id:
			stat_arbitro['ica'] = estatisticas_jogo["ica"]

	# jogos realizados
		stat_clube1['jr'] += 1
		stat_clube2['jr'] += 1
		stat_arbitro['jr'] += 1
		
		if arb_id:
			if stat_clube1['a_j'].has_key(arb_id):
				stat_clube1['a_j'][arb_id] += 1
			else:
				stat_clube1['a_j'][arb_id] = 1

			if stat_clube2['a_j'].has_key(arb_id):
				stat_clube2['a_j'][arb_id] += 1
			else:
				stat_clube2['a_j'][arb_id] = 1

			if stat_clube1['a_i'].has_key(arb_id):
				stat_clube1['a_i'][arb_id] += estatisticas_jogo["icc_clube1"]
			else:
				stat_clube1['a_i'][arb_id] = estatisticas_jogo["icc_clube1"]

			if stat_clube2['a_i'].has_key(arb_id):
				stat_clube2['a_i'][arb_id] += estatisticas_jogo["icc_clube2"]
			else:
				stat_clube2['a_i'][arb_id] = estatisticas_jogo["icc_clube2"]
				


		if stat_arbitro['c_j'].has_key(clube1_id):
			stat_arbitro['c_j'][clube1_id] += 1
		else:	
			stat_arbitro['c_j'][clube1_id] = 1

		if stat_arbitro['c_j'].has_key(clube2_id):
			stat_arbitro['c_j'][clube2_id] += 1
		else:	
			stat_arbitro['c_j'][clube2_id] = 1

		if stat_arbitro['c_i'].has_key(clube1_id):
			stat_arbitro['c_i'][clube1_id] += estatisticas_jogo["icc_clube1"]
		else:	
			stat_arbitro['c_i'][clube1_id] = estatisticas_jogo["icc_clube1"]

		if stat_arbitro['c_i'].has_key(clube2_id):
			stat_arbitro['c_i'][clube2_id] += estatisticas_jogo["icc_clube2"]
		else:	
			stat_arbitro['c_i'][clube2_id] = estatisticas_jogo["icc_clube2"]

	# para clubes:
		stat_jogo['gm'] = jogo.jog_golos_clube1 + jogo.jog_golos_clube2
		stat_clube1["gmr"] += jogo.jog_golos_clube1
		stat_clube1["gsr"] += jogo.jog_golos_clube2
		stat_clube2["gmr"] += jogo.jog_golos_clube2
		stat_clube2["gsr"] += jogo.jog_golos_clube1

		if jogo.jog_golos_clube1 > jogo.jog_golos_clube2:
			stat_clube1["vr"] += 1
			stat_clube1["pr"] += 3
			stat_clube2["dr"] += 1

		elif jogo.jog_golos_clube1  == jogo.jog_golos_clube2:
			stat_clube1["er"] += 1
			stat_clube1["pr"] += 1	
			stat_clube2["er"] += 1
			stat_clube2["pr"] += 1

		elif jogo.jog_golos_clube1 < jogo.jog_golos_clube2:
			stat_clube2["vr"] += 1
			stat_clube2["pr"] += 3
			stat_clube1["dr"] += 1
				
		stat_clube1["gmv"] += estatisticas_jogo['gv1']
		stat_clube1["gsv"] += estatisticas_jogo['gv2']
		stat_clube2["gmv"] += estatisticas_jogo['gv2']
		stat_clube2["gsv"] += estatisticas_jogo['gv1']

		# CENÁRIO VIRTUAL
		if estatisticas_jogo['gv1'] > estatisticas_jogo['gv2']:
			stat_clube1["vv"] += 1
			stat_clube1["pv"] += 3
			stat_clube2["dv"] += 1

		elif estatisticas_jogo['gv1']  == estatisticas_jogo['gv2']:
			stat_clube1["ev"] += 1
			stat_clube1["pv"] += 1
			stat_clube2["ev"] += 1
			stat_clube2["pv"] += 1

		elif estatisticas_jogo['gv1'] < estatisticas_jogo['gv2']:
			stat_clube2["vv"] += 1
			stat_clube2["pv"] += 3
			stat_clube1["dv"] += 1

	# para lances
		for lance in estatisticas_jogo["lances"]:
			stat_lance = {}

			stat_lance["dn"] = lance["dn"]
			stat_lance["clu1"] = lance["clu1"]
			stat_lance["clu2"] = lance["clu2"]
			if lance.has_key("icc1_g"):
				stat_lance["icc1_g"] = lance["icc1_g"]
			if lance.has_key("icc2_g"):
				stat_lance["icc2_g"] = lance["icc2_g"]
			stat_lance["icc1"] = lance["icc1"]
			stat_lance["icc2"] = lance["icc2"]
			stat_lance["ica"] = lance["ica"]
			
			stat_lance["d_res"] = lance["d_res"] # resultado_parcial
			stat_lance["p_res"] = lance["p_res"] # esultado_parcial
			stat_lance["d_tmp"] = lance["d_tmp"] # factor_tempo
			stat_lance["p_tmp"] = lance["p_tmp"] # factor_tempo
			stat_lance["d_ris"] = lance["d_ris"] # factor risco
			stat_lance["p_ris"] = lance["p_ris"] # factor risco
			stat_lance["d_cla"] = lance["d_cla"] # tipo, ou classe
			stat_lance["p_cla"] = lance["p_cla"] # tipo/classe do lance
			stats["lance"][lance["lan"]] = stat_lance

		# para bonus
		if estatisticas_jogo["bonus"]:
			stat_bonus={}
			stat_bonus["dn"] = estatisticas_jogo["bonus"]["dn"]
			stat_bonus["rv"] = estatisticas_jogo["bonus"]["rv"]
			stat_bonus["clu1"] = estatisticas_jogo["bonus"]["clu1"]
			stat_bonus["clu2"] = estatisticas_jogo["bonus"]["clu2"]
			stat_bonus["icc1"] = estatisticas_jogo["bonus"]["icc1"]
			stat_bonus["icc2"] = estatisticas_jogo["bonus"]["icc2"]
			stat_bonus["ica"] = estatisticas_jogo["bonus"]["ica"]
			stat_bonus["d_agr"] = estatisticas_jogo["bonus"]["d_agr"] # descrição
			stat_bonus["p_agr"] = estatisticas_jogo["bonus"]["p_agr"] # factor_agravamento
			stat_bonus["d_ris"] = estatisticas_jogo["bonus"]["d_ris"] #factor risco
			stat_bonus["p_ris"] = estatisticas_jogo["bonus"]["p_ris"] #factor risco
			stats["bonus"][jogo.key().id()] = stat_bonus

	# para cada jogador
		for jjj in jogo.jog_jogadores: 

			jogador = jjj.jjj_jogador
			clube = jjj.jjj_clube
			jgd_id = jogador.key().id()
			clu_id = clube.key().id()

		#	logging.info(u"jogador: %s " % jogador.__str__())
			stat_jogador = {}
			
			stat_jogador[clu_id] = {
			"jr":0, #jogos_realizados
			"mj":0, #minutos_jogados
			"gm":0, #golos marcados

			"ca":0, #cartoes_amarelos
			"cda":0, #cartoes duploamarelos
			"cv":0, #cartoies vermelhos

			"a_a":{}, #arbitro_amarelos
			"a_da":{}, #arbitro_duploamarelos
			"a_v": {}  #arbitro_vermelhos
			}	
			stat_jogador[clu_id]['jr'] += 1
	
		# minutos jogados 	
			minutos_jogados = 90
			if jjj.jjj_substituicao_entrada:
				if jjj.jjj_substituicao_entrada >= 90:
					minutos_jogados = jjj.jjj_substituicao_entrada - 90
				else:
					minutos_jogados = 90 - jjj.jjj_substituicao_entrada

			if jjj.jjj_substituicao_saida:
				minutos_jogados = jjj.jjj_substituicao_saida

			stat_jogador[clu_id]['mj'] = minutos_jogados
			if clu_id == clube1_id:
				stat_clube1['j_m'][jgd_id] = minutos_jogados
			else:
				stat_clube2['j_m'][jgd_id] = minutos_jogados
		
		# cartões

			if jjj.jjj_amarelo_minuto:

				stat_arbitro['ca'] += 1			
				stat_arbitro['j_a'][jgd_id] = 1
			
				if stat_arbitro['c_a'].has_key(clu_id):
					stat_arbitro['c_a'][clu_id] += 1
				else:
					stat_arbitro['c_a'][clu_id] = 1

				stat_jogo["ca"] += 1
			
				if clu_id == clube1_id:
					stat_clube1['ca'] += 1
				
					if arb_id:
						if stat_clube1['a_a'].has_key(arb_id):
							stat_clube1['a_a'][arb_id] += 1
						else:
							stat_clube1['a_a'][arb_id] = 1
					
					stat_clube1['j_a'][jgd_id] = 1
				
				else:
					stat_clube2['ca'] += 1
					if arb_id:
						if stat_clube2['a_a'].has_key(arb_id):
							stat_clube2['a_a'][arb_id] += 1
						else:
							stat_clube2['a_a'][arb_id] = 1
					
					stat_clube2['j_a'][jgd_id] = 1
		
				stat_jogador[clu_id]["ca"] += 1
				if arb_id:
					stat_jogador[clu_id]["a_a"][arb_id] = 1
		
		
			if jjj.jjj_duplo_amarelo_minuto:

				stat_arbitro['cda'] += 1			
				stat_arbitro['j_da'][jgd_id] = 1
			
				if stat_arbitro['c_da'].has_key(clu_id):
					stat_arbitro['c_da'][clu_id] += 1
				else:
					stat_arbitro['c_da'][clu_id] = 1

				stat_jogo["cda"] += 1
			
				if clu_id == clube1_id:
					stat_clube1['cda'] += 1
					if arb_id:
						if stat_clube1['a_da'].has_key(arb_id):
							stat_clube1['a_da'][arb_id] += 1
						else:
							stat_clube1['a_da'][arb_id] = 1
					
					stat_clube1['j_da'][jgd_id] = 1
				
				else:
					stat_clube2['cda'] += 1
					if arb_id:
						if stat_clube2['a_da'].has_key(arb_id):
							stat_clube2['a_da'][arb_id] += 1
						else:
							stat_clube2['a_da'][arb_id] = 1
					
					stat_clube2['j_da'][jgd_id] = 1
		
				stat_jogador[clu_id]["cda"] += 1
				if arb_id:
					stat_jogador[clu_id]["a_da"][arb_id] = 1
		
			if jjj.jjj_vermelho_minuto:
			
				stat_arbitro['cv'] += 1			
				stat_arbitro['j_v'][jgd_id] = 1
			
				if stat_arbitro['c_v'].has_key(clu_id):
					stat_arbitro['c_v'][clu_id] += 1
				else:
					stat_arbitro['c_v'][clu_id] = 1

				stat_jogo["cv"] += 1
			
				if clu_id == clube1_id:
					stat_clube1['cv'] += 1
					if arb_id:
						if stat_clube1['a_v'].has_key(arb_id):
							stat_clube1['a_v'][arb_id] += 1
						else:
							stat_clube1['a_v'][arb_id] = 1
					
					stat_clube1['j_v'][jgd_id] = 1
				
				else:
					stat_clube2['cv'] += 1
					if arb_id:
						if stat_clube2['a_v'].has_key(arb_id):
							stat_clube2['a_v'][arb_id] += 1
						else:
							stat_clube2['a_v'][arb_id] = 1
					
					stat_clube2['j_v'][jgd_id] = 1
		
				stat_jogador[clu_id]["cv"] += 1
				if arb_id:
					stat_jogador[clu_id]["a_v"][arb_id] = 1
		
			# golos
			for idx, golo in enumerate(jjj.jjj_golos_minutos):
		
				stat_jogador[clu_id]['gm'] += 1

				# verificar para que clube o golo é marcado
				if clube1_id == clu_id: 
					if jjj.jjj_golos_tipos and jjj.jjj_golos_tipos[idx] != "p.b.":
						if stat_clube1['j_g'].has_key(jgd_id):
							stat_clube1['j_g'][jgd_id] += 1
						else:
							stat_clube1['j_g'][jgd_id] = 1
					
				else:
					if jjj.jjj_golos_tipos and jjj.jjj_golos_tipos[idx] != "p.b.":
						if stat_clube2['j_g'].has_key(jgd_id):
							stat_clube2['j_g'][jgd_id] += 1
						else:
							stat_clube2['j_g'][jgd_id] = 1

			stats["jogador"][jgd_id] = stat_jogador
	
# SETTING LAST VARS
	#¬logging.info(stats["clube"].keys())
	
		stats["clube"][clube1_id] = stat_clube1
		stats["clube"][clube2_id] = stat_clube2
		if arb_id:
			stats["arbitro"][arb_id] = stat_arbitro

		stats["jogo"][jogo.key().id()] = stat_jogo

