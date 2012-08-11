# -*- coding: utf-8 -*-

from classes import *
import listas
import config
import classes

class GraficoICA:
	
	grafico = None
	
	@staticmethod
	def gera_novo_grafico_ica( stats_hash, stash_parcial, arbitros):

			arb_ids = []
			for arbitro in arbitros:
				arb_ids.append(arbitro.key().id())

			ica = {}
			resolucao = 200

			for jogo_key, jogo_values in stats_hash["jogo"].items():

				arb_id = jogo_values["arb"]
				
				if not ica.has_key(arb_id):
					ica[arb_id] = 0.0

				ica[arb_id] += jogo_values["ica"]

			temp_ica = sorted(ica, cmp=lambda x,y: cmp(ica[x], ica[y]), reverse=True)

			final_ica = []
			max_height = 0

			for arb_id in temp_ica:
				# por algum motivo, se não converter o float para str, no django ele volta a ver com carradas de decimais,
				# mesmo com o round em cima
				value = None

				# se o clube é para ter gráfico...
				if arb_id in arb_ids:

					final_ica.append({"arb":arb_id, "ica":str(round(ica[arb_id], 3)), 
				  		"height": int(round(ica[arb_id] * 1000, 3) )} )
					if abs(int(round(ica[arb_id] * 1000, 3) )) > max_height:
						max_height = abs(int(round(ica[arb_id] * 1000, 3) ))

			# avoid zero-division
			if max_height == 0:
				max_height = 400
			for item in final_ica:
				item["height"] = int ((float(item["height"]) / float(max_height))* float(resolucao))

			return final_ica
	
	def load_grafico_ica_for_epoca(self, epoca):
		acue = classes.getAcumuladorEpoca(epoca, config.VERSAO_ACUMULADOR,"ica")
		if acue:
			self.grafico = acue.acue_content["ica"]
	
	def load_grafico_ica_for_competicao(self, competicao):
		acuc = classes.getAcumuladorCompeticao(competicao, config.VERSAO_ACUMULADOR,"ica")
		if acuc:
			self.grafico = acuc.acuc_content["ica"]
		
	def get_top_bons(self, howmuch = 3):
		if self.grafico == None:
			return []
		new_grafico = self.grafico[:]
		return new_grafico[:(howmuch)]
		
	def get_top_maus(self, howmuch = 3):
		if self.grafico == None:
			return []
		new_grafico = self.grafico[:]
		new_grafico.reverse()
		return new_grafico[:(howmuch)]
