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
		
	
	#	@staticmethod
	def load_tabela_icc_for_epoca(self, epoca):
		acue = classes.getAcumuladorEpoca(epoca, config.VERSAO_ACUMULADOR,"tabela_icc")
		if acue:
			self.tabela = acue.acue_content["tabela_icc"]

	def get_top_arbitros_para_3_grandes(self):
		porto = Clube.all().filter("clu_nome = ", "Porto").get()
		benfica = Clube.all().filter("clu_nome = ", "Benfica").get()
		sporting = Clube.all().filter("clu_nome = ", "Sporting").get()
		porto_id = porto.key().id()
		benfica_id = benfica.key().id()
		sporting_id = sporting.key().id()
		
		pior_arbitro_porto = None
		melhor_arbitro_porto = None
		pior_arbitro_benfica = None
		melhor_arbitro_benfica = None
		pior_arbitro_sporting = None
		melhor_arbitro_sporting = None
		
		for idx, val in enumerate(self.tabela):
			arb_id = self.tabela[idx]["arb"]
			clus_list = self.tabela[idx]["clus"]
			for idx, val in enumerate(clus_list):
				
				if clus_list[idx]["clu"] == porto_id:
					
					if clus_list[idx]["icc"] < -0.01 or clus_list[idx]["icc"] > 0.01: # if we have something interesting:
						
						if clus_list[idx]["icc"] < -0.01:
							if pior_arbitro_porto == None:
								pior_arbitro_porto = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
							else:
								if clus_list[idx]["icc"] < pior_arbitro_porto["icc"]:
									pior_arbitro_porto = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
						if clus_list[idx]["icc"] > 0.01:
							if melhor_arbitro_porto == None:
								melhor_arbitro_porto = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
							else:
								if clus_list[idx]["icc"] < melhor_arbitro_porto["icc"]:
									melhor_arbitro_porto = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
				
				if clus_list[idx]["clu"] == benfica_id:

					if clus_list[idx]["icc"] < -0.01 or clus_list[idx]["icc"] > 0.01: # if we have something interesting:

						if clus_list[idx]["icc"] < -0.01:
							if pior_arbitro_benfica == None:
								pior_arbitro_benfica = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
							else:
								if clus_list[idx]["icc"] < pior_arbitro_benfica["icc"]:
									pior_arbitro_benfica = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
						if clus_list[idx]["icc"] > 0.01:
							if melhor_arbitro_benfica == None:
								melhor_arbitro_benfica = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
							else:
								if clus_list[idx]["icc"] < melhor_arbitro_benfica["icc"]:
									melhor_arbitro_benfica = {"arb":arb_id, "icc":clus_list[idx]["icc"]}

				if clus_list[idx]["clu"] == sporting_id:

					if clus_list[idx]["icc"] < -0.01 or clus_list[idx]["icc"] > 0.01: # if we have something interesting:
						if clus_list[idx]["icc"] < -0.01:
							if pior_arbitro_sporting == None:
								pior_arbitro_sporting = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
							else:
								if clus_list[idx]["icc"] < pior_arbitro_sporting["icc"]:
									pior_arbitro_sporting = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
						if clus_list[idx]["icc"] > 0.01:
							if melhor_arbitro_sporting == None:
								melhor_arbitro_sporting = {"arb":arb_id, "icc":clus_list[idx]["icc"]}
							else:
								if clus_list[idx]["icc"] < melhor_arbitro_sporting["icc"]:
									melhor_arbitro_sporting = {"arb":arb_id, "icc":clus_list[idx]["icc"]}

		if pior_arbitro_porto:
			pior_arbitro_porto["arb"] = Arbitro.get_by_id(pior_arbitro_porto["arb"])
		if melhor_arbitro_porto:
			melhor_arbitro_porto["arb"] = Arbitro.get_by_id(melhor_arbitro_porto["arb"])
		if pior_arbitro_benfica:
			pior_arbitro_benfica["arb"] = Arbitro.get_by_id(pior_arbitro_benfica["arb"])
		if melhor_arbitro_benfica:
			melhor_arbitro_benfica["arb"] = Arbitro.get_by_id(melhor_arbitro_benfica["arb"])
		if pior_arbitro_sporting:
			pior_arbitro_sporting["arb"] = Arbitro.get_by_id(pior_arbitro_sporting["arb"])
		if melhor_arbitro_sporting:
			melhor_arbitro_sporting["arb"] = Arbitro.get_by_id(melhor_arbitro_sporting["arb"])
		
		return [{"clu":porto, "pior_arbitro": pior_arbitro_porto, "melhor_arbitro":melhor_arbitro_porto},
			{"clu":benfica, "pior_arbitro": pior_arbitro_benfica,"melhor_arbitro":melhor_arbitro_benfica},
			{"clu":sporting, "pior_arbitro":pior_arbitro_sporting,"melhor_arbitro":melhor_arbitro_sporting}]
