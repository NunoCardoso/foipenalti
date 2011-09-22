# -*- coding: utf-8 -*-

from classes import *
import listas
import config
import classes

class GraficoICC:
	
	grafico = None
	
	# clubes dá uma lista dos clubes elegíveis para o ICC
	@staticmethod
	def gera_novo_grafico_icc( stats_hash, clubes):

			clu_ids = []
			for clube in clubes:
				clu_ids.append(clube.key().id())

			icc = {}
			resolucao = 200

			for jogo_key, jogo_values in stats_hash["jogo"].items():

				clube1_id = jogo_values["clu1"]
				clube2_id = jogo_values["clu2"]

				if not icc.has_key(clube1_id):
					icc[clube1_id] = 0.0
				if not icc.has_key(clube2_id):
					icc[clube2_id] = 0.0

				# nota: pesos de prejuízo já vêem negativos. 
				# como tal, é só adicionar tudo. 

	#			logging.info(jogo_values["icc1"])
				icc[clube1_id] += jogo_values["icc1"]
	#			logging.info(icc[clube1_id])
				icc[clube2_id] += jogo_values["icc2"]

	#		logging.info(icc)
			# converte icc numa lista. Só listas tem ordem, não as hashes.
			temp_icc = sorted(icc, cmp=lambda x,y: cmp(icc[x], icc[y]), reverse=True)

			final_icc = []
			max_height = 0

			for clube_id in temp_icc:
				# por algum motivo, se não converter o float para str, no django ele volta a ver com carradas de decimais,
				# mesmo com o round em cima
				value = None

				# se o clube é para ter gráfico...
				if clube_id in clu_ids:

					final_icc.append({"clu":clube_id, "icc":str(round(icc[clube_id], 3)), 
				  		"height": int(round(icc[clube_id] * 1000, 3) )} )
					if abs(int(round(icc[clube_id] * 1000, 3) )) > max_height:
						max_height = abs(int(round(icc[clube_id] * 1000, 3) ))

			# avoid zero-division
			if max_height == 0:
				max_height = 400
			for item in final_icc:
				item["height"] = int ((float(item["height"]) / float(max_height))* float(resolucao))

			return final_icc
	
#	@staticmethod
	def load_grafico_icc_for_epoca(self, epoca):
		acue = classes.getAcumuladorEpoca(epoca, config.VERSAO_ACUMULADOR,"icc")
		if acue:
			self.grafico = acue.acue_content["icc"]
		
	def get_top_beneficiados(self, howmuch = 3):
		new_grafico = self.grafico[:]
		return new_grafico[:(howmuch)]
		
	def get_top_prejudicados(self, howmuch = 3):
		new_grafico = self.grafico[:]
		new_grafico.reverse()
		return new_grafico[:(howmuch)]