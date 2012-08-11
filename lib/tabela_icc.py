# -*- coding: utf-8 -*-

from classes import *
import listas
import classes
import config

class TabelaICC:
	
	tabela = None
	
	# só primodivisionários
	# a lista de clubes vem com os primodivisionários ordenados por popularidade (classificação é arriscado por agora) 
	
	@staticmethod
	def gera_nova_tabela_icc(stats_hash, clubes):

		arbitro_clube_stats = {}

		for jogo_key, jogo_values in stats_hash["jogo"].items():

			arb_id = None

			if jogo_values.has_key("arb"):
				arb_id = jogo_values["arb"]
				if not arbitro_clube_stats.has_key(arb_id):
					arbitro_clube_stats[arb_id] = {"icc":0, "jr":0, "clus":{}}

				arbitro_clube_stats[arb_id]["jr"] += 1 
				arbitro_clube_stats[arb_id]["icc"] += abs(jogo_values["icc1"]) 

				cl1 = jogo_values["clu1"]
				if not arbitro_clube_stats[arb_id]["clus"].has_key(cl1):
					arbitro_clube_stats[arb_id]["clus"][cl1] = jogo_values["icc1"]
				else: 
					arbitro_clube_stats[arb_id]["clus"][cl1] += jogo_values["icc1"]

				cl2 = jogo_values["clu2"]
				if not arbitro_clube_stats[arb_id]["clus"].has_key(cl2):
					arbitro_clube_stats[arb_id]["clus"][cl2] = jogo_values["icc2"]
				else: 
					arbitro_clube_stats[arb_id]["clus"][cl2] += jogo_values["icc2"]

		# vamos ordenar clubes em cada árbitro
		for arb_id, values in arbitro_clube_stats.items():

			lista_temp = []

			# preencher clubes com ICC vazios
			for clube in clubes:
				if not arbitro_clube_stats[arb_id]["clus"].has_key(clube.key().id()):
					arbitro_clube_stats[arb_id]["clus"][clube.key().id()] = 0.0

			for clube in clubes:
				clu_id = clube.key().id()
				lista_temp.append({"clu":clu_id, "icc":arbitro_clube_stats[arb_id]["clus"][clu_id] })

			# substitui a hash inicial por uma lista
			arbitro_clube_stats[arb_id]["clus"] = lista_temp

		arbitro_clube_list = []
		list_order = sorted(arbitro_clube_stats, cmp=lambda x,y: cmp(arbitro_clube_stats[x]["icc"], arbitro_clube_stats[y]["icc"]), reverse=True) 

		for arb_id in list_order:
			arbitro_clube_stats[arb_id]["arb"] = arb_id
			arbitro_clube_list.append(arbitro_clube_stats[arb_id])

		return arbitro_clube_list
		
	
	def load_tabela_icc_for_epoca(self, epoca):
		acue = classes.getAcumuladorEpoca(epoca, config.VERSAO_ACUMULADOR,"tabela_icc")
		if acue:
			self.tabela = acue.acue_content["tabela_icc"]

	def load_tabela_icc_for_competicao(self, competicao):
		acuc = classes.getAcumuladorCompeticao(competicao, config.VERSAO_ACUMULADOR,"tabela_icc")
		if acuc:
			self.tabela = acuc.acuc_content["tabela_icc"]

	def get_top_arbitros_para_3_grandes(self):
		
		clubes = ["Porto", "Benfica", "Sporting", "Braga"]

		for idx, val in enumerate(clubes):
			
			clube = Clube.all().filter("clu_nome = ", clubes[idx]).get()
			clube_id = clube.key().id()
			clubes[idx] = {"clube":clube, "clube_id":clube_id, "pior_arbitro":None, "melhor_arbitro":None}
		
		if self.tabela == None:
			return []
		for idx, val in enumerate(self.tabela):

			arb_id = self.tabela[idx]["arb"]
			clus_list = self.tabela[idx]["clus"]

			for idx, val in enumerate(clus_list):
				
				for idx2, val2 in enumerate(clubes):
				
					if clus_list[idx]["clu"] == clubes[idx2]["clube_id"]:
					
						if clus_list[idx]["icc"] < -0.01 or clus_list[idx]["icc"] > 0.01: # if we have something interesting:
						
							if clus_list[idx]["icc"] < -0.01:
								
								if clubes[idx2]["pior_arbitro"] == None:
									clubes[idx2]["pior_arbitro"] = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
								else:
									if clus_list[idx]["icc"] < clubes[idx2]["pior_arbitro"]["icc"]:
										clubes[idx2]["pior_arbitro"] = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
										
							if clus_list[idx]["icc"] > 0.01:
								if clubes[idx2]["melhor_arbitro"] == None:
									clubes[idx2]["melhor_arbitro"] = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
								else:
									if clus_list[idx]["icc"] < clubes[idx2]["melhor_arbitro"]["icc"]:
										clubes[idx2]["melhor_arbitro"] = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
		
		for idx, val in enumerate(clubes):
			if clubes[idx]["pior_arbitro"]:
				clubes[idx]["pior_arbitro"]["arb"] = Arbitro.get_by_id(clubes[idx]["pior_arbitro"]["arb"])
			if clubes[idx]["melhor_arbitro"]:
				clubes[idx]["melhor_arbitro"]["arb"] = Arbitro.get_by_id(clubes[idx]["melhor_arbitro"]["arb"])

		return clubes
