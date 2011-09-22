# -*- coding: utf-8 -*-

from classes import *
import listas
	
#####################
## GERA TOP CLUBES ##
#####################

def gera_top_clubes(stats_hash):
	
	top_list_big = 30
	top_list_small = 10
	
	# se alterar aqui, tenho de estabelecer regras de ordenação no do_it do 
	# acumulador_epoca.py
	top_clubes_dados = {
	 "mais_indisciplinados":[],
	 "mais_golos_marcados_e_validados_com_erro_arbitro":[],
	 "mais_golos_sofridos_e_validados_com_erro_arbitro":[],
	 "mais_golos_marcados_e_invalidados_com_erro_arbitro":[],
	 "mais_golos_sofridos_e_invalidados_com_erro_arbitro":[],
	 "saldo_golos":[],
	 "mais_pontos_ganhos_com_erro_arbitro":[],
	 "mais_pontos_perdidos_com_erro_arbitro":[],
	 "saldo_pontos":[],
	 "mais_icc":[]
	}
	
	golos_marcados_e_validados_com_erro_arbitro = {}
	golos_sofridos_e_validados_com_erro_arbitro = {}
	golos_marcados_e_invalidados_com_erro_arbitro = {} # mal anulados
	golos_sofridos_e_invalidados_com_erro_arbitro = {} # mal anulados
	saldo_golos = {}
	
	pontos_ganhos = {}
	pontos_perdidos = {}
	saldo_pontos = {}
	
	indisciplina = {}
	icc = {}
	
	for jogo_key, jogo_values in stats_hash["jogo"].items():
		
		cl1_id = jogo_values["clu1"]
		cl2_id = jogo_values["clu2"]
		
		if not icc.has_key(cl1_id):
			 icc[cl1_id] = 0.0
		if not icc.has_key(cl2_id):
			 icc[cl2_id] = 0.0

		# reset golos_marcados
		if not golos_marcados_e_validados_com_erro_arbitro.has_key(cl1_id):
			 golos_marcados_e_validados_com_erro_arbitro[cl1_id] = 0
		if not golos_marcados_e_validados_com_erro_arbitro.has_key(cl2_id):
			 golos_marcados_e_validados_com_erro_arbitro[cl2_id] = 0

		# reset golos_sofridos
		if not golos_sofridos_e_validados_com_erro_arbitro.has_key(cl1_id):
			 golos_sofridos_e_validados_com_erro_arbitro[cl1_id] = 0
		if not golos_sofridos_e_validados_com_erro_arbitro.has_key(cl2_id):
			 golos_sofridos_e_validados_com_erro_arbitro[cl2_id] = 0
				
		# reset golos_marcados
		if not golos_marcados_e_invalidados_com_erro_arbitro.has_key(cl1_id):
			 golos_marcados_e_invalidados_com_erro_arbitro[cl1_id] = 0
		if not golos_marcados_e_invalidados_com_erro_arbitro.has_key(cl2_id):
			 golos_marcados_e_invalidados_com_erro_arbitro[cl2_id] = 0
				
		# reset golos_sofridos
		if not golos_sofridos_e_invalidados_com_erro_arbitro.has_key(cl1_id):
			 golos_sofridos_e_invalidados_com_erro_arbitro[cl1_id] = 0
		if not golos_sofridos_e_invalidados_com_erro_arbitro.has_key(cl2_id):
			 golos_sofridos_e_invalidados_com_erro_arbitro[cl2_id] = 0

		# reset saldo golos
		if not saldo_golos.has_key(cl1_id):
			 saldo_golos[cl1_id] = 0
		if not saldo_golos.has_key(cl2_id):
			 saldo_golos[cl2_id] = 0
				
		# reset pontos_ganhos
		if not pontos_ganhos.has_key(cl1_id):
			 pontos_ganhos[cl1_id] = 0
		if not pontos_ganhos.has_key(cl2_id):
			 pontos_ganhos[cl2_id] = 0
				
		# reset pontos_perdidos
		if not pontos_perdidos.has_key(cl1_id):
			 pontos_perdidos[cl1_id] = 0
		if not pontos_perdidos.has_key(cl2_id):
			 pontos_perdidos[cl2_id] = 0

		# reset saldo_pontos
		if not saldo_pontos.has_key(cl1_id):
			 saldo_pontos[cl1_id] = 0
		if not saldo_pontos.has_key(cl2_id):
			 saldo_pontos[cl2_id] = 0

			
		if not indisciplina.has_key(cl1_id):
			indisciplina[cl1_id] = {"tot":0, "ca":0, "cda":0, "cv":0}
		if not indisciplina.has_key(cl2_id):
			indisciplina[cl2_id] = {"tot":0, "ca":0, "cda":0, "cv":0}	
		
		icc[cl1_id] += jogo_values["icc1"]
		icc[cl2_id] += jogo_values["icc2"]
			
		if jogo_values["gv1"] != None and \
			jogo_values["go1"] != None and \
			jogo_values["gv2"] != None and \
			jogo_values["go2"] != None:
			# diferencial golos reais vs golos virtualsi clube 1
			diff_golos_cl1 = jogo_values["gv1"] - jogo_values["go1"]
			# se há mais golos origniais que virtuais, é porque houve golos ilegais validados no jogo
			if diff_golos_cl1 < 0:
				golos_marcados_e_validados_com_erro_arbitro[cl1_id] += abs(diff_golos_cl1)
				golos_sofridos_e_validados_com_erro_arbitro[cl2_id] += abs(diff_golos_cl1)
			# se há mais golos virtuais que originais, é porque houve golos legais invalidados no jogo	
			if diff_golos_cl1 > 0:	
				golos_marcados_e_invalidados_com_erro_arbitro[cl1_id] += diff_golos_cl1
				golos_sofridos_e_invalidados_com_erro_arbitro[cl2_id] += diff_golos_cl1
				
			diff_golos_cl2 = jogo_values["gv2"] - jogo_values["go2"]
			# se há mais golos origniais que virtuais, é porque houve golos ilegais validados no jogo
			if diff_golos_cl2 < 0:
				golos_marcados_e_validados_com_erro_arbitro[cl2_id] += abs(diff_golos_cl2)
				golos_sofridos_e_validados_com_erro_arbitro[cl1_id] += abs(diff_golos_cl2)
			# se há mais golos virtuais que originais, é porque houve golos legais invalidados no jogo
			if diff_golos_cl2 > 0:	
				golos_marcados_e_invalidados_com_erro_arbitro[cl2_id] += diff_golos_cl2
				golos_sofridos_e_invalidados_com_erro_arbitro[cl1_id] += diff_golos_cl2
				
			# saldo_golos - positivo = mais golos benefiados que golos prejudicados
			saldo_golos[cl1_id] += diff_golos_cl1
			saldo_golos[cl2_id] += diff_golos_cl2
			
			# diferencial pontos reais vs pontos virtualsi clube 1
			diff_pontos_cl1 =  jogo_values["po1"] - jogo_values["pv1"]
			diff_pontos_cl2 = jogo_values["po2"] - jogo_values["pv2"]
			# se há mais golos origniais que virtuais, é porque houve golos ilegais validados no jogo
			if diff_pontos_cl1 > 0:
				pontos_ganhos[cl1_id] += diff_pontos_cl1
			if diff_pontos_cl1 < 0:
				pontos_perdidos[cl1_id] += abs(diff_pontos_cl1)
			if diff_pontos_cl2 > 0:
				pontos_ganhos[cl2_id] += diff_pontos_cl2
			if diff_pontos_cl2 < 0:
				pontos_perdidos[cl2_id] += abs(diff_pontos_cl2)
				
			# saldo_pontos - cuidado, no final pode ser valor negativo 
			saldo_pontos[cl1_id] += diff_pontos_cl1
			saldo_pontos[cl2_id] += diff_pontos_cl2
		
# INDISCIPLINA - pode-ser iterar clubes, é + rápido
	for clube_key, clube_values in stats_hash["clube"].items():
		if not indisciplina.has_key(clube_key):
			indisciplina[clube_key] = {"ca":0, "cda":0, "cv":0, "tot":0}
		indisciplina[clube_key]["ca"] += clube_values["ca"] 
		indisciplina[clube_key]["cda"] += clube_values["cda"] 
		indisciplina[clube_key]["cv"] += clube_values["cv"] 
		indisciplina[clube_key]["tot"] += clube_values["ca"] + 1.5* clube_values["cda"] + 2*clube_values["cv"] 
	
	indisciplina_order = sorted(indisciplina, cmp=lambda x,y: \
		cmp(indisciplina[x]["tot"], indisciplina[y]["tot"] ), reverse=True )
	
	howmany = len(indisciplina_order) if len(indisciplina_order) <= top_list_big else top_list_big
	for clube_id in indisciplina_order[:howmany]:
		top_clubes_dados["mais_indisciplinados"].append({
			"clu":clube_id,
			"crt":indisciplina[clube_id]
	})

# GOLOS MARCADOS / SOFRIDOS VALIDADOS / INVALIDADOS 

	# MARCADOS / VALIDADOS
	mais_golos_marcados_e_validados_order = sorted(golos_marcados_e_validados_com_erro_arbitro, \
		cmp=lambda x,y: cmp(golos_marcados_e_validados_com_erro_arbitro[x], \
			golos_marcados_e_validados_com_erro_arbitro[y]), reverse=True )

	howmany = len(mais_golos_marcados_e_validados_order) if \
		len(mais_golos_marcados_e_validados_order) <= top_list_small else top_list_small
	
	for clube_id in mais_golos_marcados_e_validados_order[:howmany]:
		top_clubes_dados["mais_golos_marcados_e_validados_com_erro_arbitro"].append({
			"clu":clube_id,
			"gol":golos_marcados_e_validados_com_erro_arbitro[clube_id]
	})

	# SOFRIDOS / VALIDADOS
	mais_golos_sofridos_e_validados_order = sorted(golos_sofridos_e_validados_com_erro_arbitro, \
		cmp=lambda x,y: cmp(golos_sofridos_e_validados_com_erro_arbitro[x], \
			golos_sofridos_e_validados_com_erro_arbitro[y]), reverse=True )

	howmany = len(mais_golos_sofridos_e_validados_order) if \
		len(mais_golos_sofridos_e_validados_order) <= top_list_small else top_list_small
	
	for clube_id in mais_golos_sofridos_e_validados_order[:howmany]:
		top_clubes_dados["mais_golos_sofridos_e_validados_com_erro_arbitro"].append({
			"clu":clube_id,
			"gol":golos_sofridos_e_validados_com_erro_arbitro[clube_id]
	})

	# MARCADOS / INVALIDADOS	
	mais_golos_marcados_e_invalidados_order = sorted(golos_marcados_e_invalidados_com_erro_arbitro, \
		cmp=lambda x,y: cmp(golos_marcados_e_invalidados_com_erro_arbitro[x], \
			golos_marcados_e_invalidados_com_erro_arbitro[y]), reverse=True )

	howmany = len(mais_golos_marcados_e_invalidados_order) if \
		len(mais_golos_marcados_e_invalidados_order) <= top_list_small else top_list_small
	
	for clube_id in mais_golos_marcados_e_invalidados_order[:howmany]:
		top_clubes_dados["mais_golos_marcados_e_invalidados_com_erro_arbitro"].append({
			"clu":clube_id,
			"gol":golos_marcados_e_invalidados_com_erro_arbitro[clube_id]
	})
	
	# SOFRIDOS / INVALIDADOS
	mais_golos_sofridos_e_invalidados_order = sorted(golos_sofridos_e_invalidados_com_erro_arbitro, \
		cmp=lambda x,y: cmp(golos_sofridos_e_invalidados_com_erro_arbitro[x], \
			golos_sofridos_e_invalidados_com_erro_arbitro[y]), reverse=True )
			
	howmany = len(mais_golos_sofridos_e_invalidados_order) if \
		len(mais_golos_sofridos_e_invalidados_order) <= top_list_small else top_list_small
	
	for clube_id in mais_golos_sofridos_e_invalidados_order[:howmany]:
		top_clubes_dados["mais_golos_sofridos_e_invalidados_com_erro_arbitro"].append({
			"clu":clube_id,
			"gol":golos_sofridos_e_invalidados_com_erro_arbitro[clube_id]
	})

	# SALDO GOLOS
	saldo_golos_order = sorted(saldo_golos, cmp=lambda x,y: \
		cmp(saldo_golos[x], saldo_golos[y] ), reverse=True )
	
	howmany = len(saldo_golos_order) if len(saldo_golos_order) <= top_list_big else top_list_big
	for clube_id in saldo_golos_order[:howmany]:
		top_clubes_dados["saldo_golos"].append({
			"clu":clube_id,
			"gol":saldo_golos[clube_id]
	})

	# TOP PONTOS
	pontos_ganhos_order = sorted(pontos_ganhos, cmp=lambda x,y: \
		cmp(pontos_ganhos[x], pontos_ganhos[y] ), reverse=True )

	pontos_perdidos_order = sorted(pontos_perdidos, cmp=lambda x,y: \
		cmp(pontos_perdidos[x], pontos_perdidos[y] ), reverse=True)
	
	howmany = len(pontos_ganhos_order) if len(pontos_ganhos_order) <= top_list_small else top_list_small
	for clube_id in pontos_ganhos_order[:howmany]:
		top_clubes_dados["mais_pontos_ganhos_com_erro_arbitro"].append({
			"clu":clube_id,
			"p":pontos_ganhos[clube_id]
	})
	howmany = len(pontos_perdidos_order) if len(pontos_perdidos_order) <= top_list_small else top_list_small
	for clube_id in pontos_perdidos_order[:howmany]:
		top_clubes_dados["mais_pontos_perdidos_com_erro_arbitro"].append({
			"clu":clube_id,
			"p":pontos_perdidos[clube_id]
	})
	
	# TOP SALDO PONTOS

	saldo_pontos_order = sorted(saldo_pontos, cmp=lambda x,y: \
		cmp(saldo_pontos[x], saldo_pontos[y] ), reverse=True )

	howmany = len(saldo_pontos_order) if len(saldo_pontos_order) <= top_list_big else top_list_big
	for clube_id in saldo_pontos_order[:howmany]:
		top_clubes_dados["saldo_pontos"].append({
			"clu":clube_id,
			"p":saldo_pontos[clube_id]
	})

	# TOP ICC

	sort = sorted(icc, cmp=lambda x,y: cmp(icc[x], icc[y]), reverse=True)
	howmany = len(sort) if len(sort) <= top_list_big else top_list_big
	
	for clube_id in sort[:howmany]:			
		if icc[clube_id] > 0: 
			top_clubes_dados["mais_icc"].append({
				"clu":clube_id,
				"icc":icc[clube_id]
			}) 
		
	return top_clubes_dados

#######################
## GERA TOP ARBITROS ##
#######################

def gera_top_arbitros(stats_hash):
	# nota: jor_numero é um str, ordenar com .order("jor_numero") dá ordem de string	
	top_list = 100
	
	# se alterar aqui, tenho de estabelecer regras de ordenação no do_it do 
	# acumulador_epoca.py
	top_arbitros_dados = {
		"cartoes_mostrados":[],
		"mais_icc":[]
	}
	
	jogos = {}
	cartoes_mostrados = {}
	icc = {}
	
	for jogo_key, jogo_values in stats_hash["jogo"].items():
		#logging.info(jogo_values)
	
		arb_id = None
		if jogo_values.has_key("arb"):
			arb_id = jogo_values["arb"]
		
		if arb_id:	
			if jogos.has_key(arb_id):
				jogos[arb_id] += 1 
			else:
				jogos[arb_id] = 1
			
			if not icc.has_key(arb_id):
				icc[arb_id] = 0
			icc[arb_id] += abs(jogo_values['icc1'])
			
			#logging.info(arb_id)

	for arbitro_key, arbitro_values in stats_hash["arbitro"].items():
		#logging.info(arbitro_key)
		if not cartoes_mostrados.has_key(arbitro_key):
			cartoes_mostrados[arbitro_key] = {"tot":0, "ca":0, "cda":0, "cv":0}
			
		cartoes_mostrados[arbitro_key]["ca"] += arbitro_values["ca"] 
		cartoes_mostrados[arbitro_key]["cda"] += arbitro_values["cda"] 
		cartoes_mostrados[arbitro_key]["cv"] += arbitro_values["cv"] 
		cartoes_mostrados[arbitro_key]["tot"] += arbitro_values["ca"] + 1.5* arbitro_values["cda"] + 2*arbitro_values["cv"] 

	cartoes_mostrados_order = sorted(cartoes_mostrados, cmp=lambda x,y: \
		cmp(cartoes_mostrados[x]["tot"], cartoes_mostrados[y]["tot"] ), reverse=True )
	
	icc_order = sorted(icc, cmp=lambda x,y: cmp(icc[x], icc[y]), reverse=True )

	howmany = len(cartoes_mostrados_order) if len(cartoes_mostrados_order) <= top_list else top_list
	for arbitro_id in cartoes_mostrados_order[:howmany]:
		top_arbitros_dados["cartoes_mostrados"].append({
			"arb":arbitro_id,
			"jr":jogos[arbitro_id],
			"crt":cartoes_mostrados[arbitro_id]
		})

	howmany = len(icc_order) if len(icc_order) <= top_list else top_list
	for arbitro_id in icc_order[:howmany]:
		top_arbitros_dados["mais_icc"].append({
			"arb":arbitro_id,
			"jr":jogos[arbitro_id],
			"icc":icc[arbitro_id]
		})
	
	return top_arbitros_dados	

########################
## GERA TOP JOGADORES ##
########################
	
def gera_top_jogadores(stats_hash, competicao):
	
	top_list = 100
	
	# se alterar aqui, tenho de estabelecer regras de ordenação no do_it do 
	# acumulador_epoca.py
	top_jogadores_dados = {
	 "mais_cartoes":[],
	 "mais_golos":[],
	 "mais_lances":[]
	}
	
	cartoes = {}
	golos = {}
	lances = {}
	
	numero_cartoes = {}
	
	# isto é muito exigente do ponto de vista computacional. É melhor fazer uma truncagem.
	#logging.info("A percorrer jogadores todos")

	for jogador_key, clubes in stats_hash["jogador"].items():
		cartoes[jogador_key] = {"tot":0, "ca":0, "cda":0, "cv":0}
		golos[jogador_key] = 0
		for clube_key, clube_values in clubes.items():
			total = clube_values["ca"] + 1.5*clube_values["cda"] + 2*clube_values["cv"]
			if total > 0:
				cartoes[jogador_key]["ca"] += clube_values["ca"]
				cartoes[jogador_key]["cda"] += clube_values["cda"]
				cartoes[jogador_key]["cv"] += clube_values["cv"]
				cartoes[jogador_key]["tot"] += total
			
			if clube_values["gm"] > 0:
				golos[jogador_key] += clube_values["gm"]
				# if jogador_key == 143L:
				# 	logging.info("Cardozo:")
				# 	logging.info(golos[jogador_key])
				# 	logging.info(clube_values["gm"])
				
	logging.info("A percorrer jels todos")
	# agora, vamos à BD e percorrer todos os JEL		



	for lance in Lance.all().filter("lan_competicao = ", competicao):
		for jels in lance.lan_jogadores:
			jgd_id = jels.jel_jogador.key().id()
	 		if not lances.has_key(jgd_id):
				lances[jgd_id] = 0
	 		lances[jgd_id] += 1

				
	#logging.info(lances)
	mais_cartoes_order = sorted(cartoes, cmp=lambda x,y: \
		cmp(cartoes[x]["tot"], cartoes[y]["tot"] ), reverse=True )
	
	mais_golos_order = sorted(golos, cmp=lambda x,y: cmp(golos[x], golos[y] ), reverse=True )
	
	mais_lances_order = sorted(lances, cmp=lambda x,y: cmp(lances[x], lances[y] ), reverse=True )

	howmany = len(mais_cartoes_order) if len(mais_cartoes_order) <= top_list else top_list
	for jogador_id in mais_cartoes_order[:howmany]:
		if cartoes[jogador_id]["tot"] > 0:
			top_jogadores_dados["mais_cartoes"].append({
				"jgd":jogador_id,
				"crt":cartoes[jogador_id]
			})

	howmany = len(mais_golos_order) if len(mais_golos_order) <= top_list else top_list
	for jogador_id in mais_golos_order[:howmany]:
		if golos[jogador_id] > 0:
			top_jogadores_dados["mais_golos"].append({
			"jgd":jogador_id,
			"gol":golos[jogador_id]
			})

	howmany = len(mais_lances_order) if len(mais_lances_order) <= top_list else top_list
	for jogador_id in mais_lances_order[:howmany]:
		top_jogadores_dados["mais_lances"].append({
			"jgd":jogador_id,
			"num":lances[jogador_id]
	})
	
	return top_jogadores_dados	

####################
## GERA TOP JOGOS ##
####################
	
def gera_top_jogos(stats_hash):	
	# nota: jor_numero é um str, ordenar com .order("jor_numero") dá ordem de string
	
	top_list = 100
	
	# se alterar aqui, tenho de estabelecer regras de ordenação no do_it do 
	# acumulador_epoca.py
	top_jogos_dados = {
	 "mais_golos":[],
	 "maiores_goleadas":[],
	 "mais_indisciplina":[],
	 "mais_icc":[]
	}
	
	mais_golos = {}
	maiores_goleadas = {}
	mais_indisciplina = {}
	mais_icc = {}
	
	for jogo_key, jogo_values in stats_hash["jogo"].items():
		
		if jogo_values["go1"] != None and jogo_values["go2"] != None:	
			mais_golos[jogo_key] = jogo_values["go1"] + jogo_values["go2"] 
			maiores_goleadas[jogo_key] = abs(jogo_values["go1"] - jogo_values["go2"]) 

			mais_indisciplina[jogo_key] = {
			"ca":jogo_values["ca"], 
			"cda":jogo_values["cda"], 
			"cv":jogo_values["cv"],
			"tot":jogo_values["ca"]+1.5*jogo_values["cda"]+2*jogo_values["cv"]
			}
			
			mais_icc[jogo_key] = abs(jogo_values['icc1'])
			
	mais_golos_order = sorted(mais_golos, cmp=lambda x,y: \
		cmp(mais_golos[x], mais_golos[y]) )
	maiores_goleadas_order = sorted(maiores_goleadas, cmp=lambda x,y: \
		cmp(maiores_goleadas[x], maiores_goleadas[y]) )
	mais_indisciplina_order = sorted(mais_indisciplina, cmp=lambda x,y: \
		cmp(mais_indisciplina[x]["tot"], mais_indisciplina[y]["tot"] ) )
	mais_icc_order = sorted(mais_icc, cmp=lambda x,y: \
		cmp(mais_icc[x], mais_icc[y]) )

	mais_golos_order.reverse()
	howmany = len(mais_golos_order) if len(mais_golos_order) <= top_list else top_list
	for jogo_key in mais_golos_order[:howmany]:
		top_jogos_dados["mais_golos"].append({
			"jog":jogo_key,
			"gol":mais_golos[jogo_key]
		})

	maiores_goleadas_order.reverse()
	howmany = len(maiores_goleadas_order) if len(maiores_goleadas_order) <= top_list else top_list
	for jogo_key in maiores_goleadas_order[:howmany]:
		top_jogos_dados["maiores_goleadas"].append({
			"jog":jogo_key,
			"dif":maiores_goleadas[jogo_key]
		})
		
	mais_indisciplina_order.reverse()
	howmany = len(mais_indisciplina_order) if len(mais_indisciplina_order) <= top_list else top_list
	for jogo_key in mais_indisciplina_order[:howmany]:
		top_jogos_dados["mais_indisciplina"].append({
			"jog":jogo_key,
			"crt":mais_indisciplina[jogo_key]
		})
		
	mais_icc_order.reverse()
	howmany = len(mais_icc_order) if len(mais_icc_order) <= top_list else top_list
	for jogo_key in mais_icc_order[:howmany]:
		top_jogos_dados["mais_icc"].append({
			"jog":jogo_key,
			"icc":mais_icc[jogo_key]
		})
		
	return top_jogos_dados	
	