# -*- coding: utf-8 -*-

from classes import *
import listas
import config
import classes

class DetalheICC:
	
	detalhe = None
	lista_lances = None
	clube = None
	epoca = None
	
	def setLances(self, lista_lances):
		self.lista_lances = lista_lances
		
	def setClube(self, clube):
		self.clube = clube

	def setAcumuladoresJornadas(self, acu_jornadas):
		self.acu_jornadas = acu_jornadas
		
	def gera(self):
	
		# obter acumuladores jornada, para aceder à info de lances e bonus
		total_icc_beneficio = 0.0
		total_icc_prejuizo = 0.0
		jogos = {}		

		for lance in self.lista_lances:
		
			jog_id = lance.lan_jogo.key().id()
			lan_id = lance.key().id()
			clu_id = None
			
			if self.clube:
				clu_id = self.clube.key().id()
		
			if not jogos.has_key(jog_id):
				jogos[jog_id] = {
				"jogo":lance.lan_jogo,
				"lances":[],
				"bonus":None
				}
		
			lance_hash = None
			bonuss = None
		
			if self.acu_jornadas.has_key(lance.lan_jornada.jor_nome):
				acu = self.acu_jornadas[lance.lan_jornada.jor_nome]
				if acu.has_key("lance") and acu["lance"].has_key(lan_id):
					lance_hash = acu["lance"][lan_id]
				
				# adicionar o bónus se existir, só uma vez (1 por jogo)	
				if jogos[jog_id]["bonus"] == None and \
					acu.has_key("bonus") and acu["bonus"].has_key(jog_id):
					jogos[jog_id]["bonus"] = acu["bonus"][jog_id]

				# adicionar o jogo	
				if jogos[jog_id]["jogo"] == None:
					jogos[jog_id]["jogo"] = lance.lan_jogo
		
			# vamos ligar só a lances que possuem benefícios
			if lance_hash:
			
				# vamos aproveitar e enriquecer as hashes vindas do AcumuladorJornada
				# com info da BD
				lance_hash["id"] = lan_id
				lance_hash["descricao"] = lance.lan_descricao
				lance_hash["num"] = lance.lan_numero
				lance_hash["min"] = lance.lan_minuto
			
				if lance_hash["dn"] == Lance.translation_julgamento_arbitro.index(
				'Beneficiou a equipa da casa'):
				
					jogos[jog_id]["lances"].append(lance_hash)
					if clu_id:
						if lance_hash["clu1"] == clu_id:
							total_icc_beneficio += lance_hash["icc1"]
						elif lance_hash["clu2"] == clu_id:
							total_icc_beneficio += lance_hash["icc2"]
			
				elif lance_hash["dn"] == Lance.translation_julgamento_arbitro.index(
					'Beneficiou a equipa visitante'):
					jogos[jog_id]["lances"].append(lance_hash)
					
					if clu_id:
						if lance_hash["clu1"] == clu_id:
							total_icc_prejuizo += lance_hash["icc1"]
						elif lance_hash["clu2"] == clu_id:
							total_icc_prejuizo += lance_hash["icc2"]
		
		# let's sort lances by lan_numero, that should do it! :)
		# jogos mais recentes vão para a frente
		jogos = sorted(jogos.values(), cmp=lambda x,y: cmp(x["jogo"].jog_data, y["jogo"].jog_data), reverse=True) 
		
		return {"jogos":jogos,
		"total_icc_beneficio":total_icc_beneficio,
		"total_icc_prejuizo":total_icc_prejuizo
	 	}
	
	# como total_icc_prejuizo é negativo, basta adicionar os dois para fazer a tal "subtracção"
	
	
