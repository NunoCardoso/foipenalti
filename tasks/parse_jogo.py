# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import urlfetch

import os
import datetime
import logging
import re
import config 
import urllib
import traceback
from lib import listas

from django.utils import simplejson

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler
from externals.parse_maisfutebol import ParseMaisFutebol


class ParseJogo(MyHandler):
	
	# MaisFutebol -> Foipenalti
	clubes_hash={
	'Académica':'Academica',
	'Beira Mar':'BeiraMar',
	'Benfica':'Benfica',
	'Feirense':'Feirense',
	'F.C. Porto':'Porto',
	'Gil Vicente':'GilVicente',
	'Marítimo':'Maritimo',
	'Nacional':'Nacional',
	'Olhanense':'Olhanense',
	'P. Ferreira':'PacosFerreira',
	'Rio Ave':'RioAve',
	'Sporting':'Sporting',
	'Sp. Braga':'Braga',
	'U. Leiria':'Leiria',
	'V. Guimarães':'Guimaraes',
	'V. Setúbal':'Setubal',
        'Moreirense':'Moreirense',
        'Estoril':'Estoril'
	} 
	
	def get(self):
		
		url = self.request.get("url")
		logging.info("A ler o URL "+url)
		
		messages = []
		self.response.headers['Content-Type'] = "application/json"

		if url: 
			try:
				url = urllib.unquote_plus(url) 
			except:
				pass
				
		if not url:
			message = u"Erro: URL %s não é válido" % url
			logging.error(message)
			return self.response.out.write(simplejson.dumps({'status':'Erro', 'message':message}))
		
		response = None
		html = None
		
		# MAISFUTEBOL
		if url.startswith("http://www.maisfutebol.iol.pt"):
			try:
				html =  urlfetch.fetch(url)
			except:
				message = u"Erro: URL %s nao consegue ser lido" % url
				logging.error(message)
				return self.response.out.write(simplejson.dumps({'status':'Erro', 'message':message}))

			if html and html.status_code == 200:
				try:
					p = ParseMaisFutebol()
					response = p.parse(html.content)
					#logging.info(response)
					if response["status"] == "OK":
						logging.info("Parse MaisFutebol OK. Li %s bytes." % len(html.content))
					else:
						logging.error("Parse MaisFutebol FAIL: ")
						logging.error(response["message"])
						return self.response.out.write(simplejson.dumps(
							{'status':'Error', 'message':simplejson.dumps(response["message"])}))
						
				except:
					logging.error("Erro no ParseMaisFutebol:")
					trace = "".join(traceback.format_exc())
					logging.error(trace)

		if response.has_key("message"):
			results = response["message"]
		if results:
			return self.parse(results)

	def parse(self, results):
			output = {}
			logging.info("Tenho resultados MaisFutebol em hash, a converter para FoiPenalti")
			clube1 = Clube.all().filter("clu_nome = ", self.clubes_hash[results["clube1"]]).get()
			if not clube1:
				message = u"Não sei que clube é: %s " % results["clube1"]
				logging.error(message)
				return self.response.out.write(simplejson.dumps({'status':'Erro', 'message':message}))

			clube2 = Clube.all().filter("clu_nome = ", self.clubes_hash[results["clube2"]]).get()
			if not clube2:
				message = u"Não sei que clube é: %s " % results["clube2"]
				logging.error(message)
				return self.response.out.write(simplejson.dumps({'status':'Erro', 'message':message}))

			logging.info("Clubes detectados")

			arbitro = None
			if results.has_key("arbitro"):
				arbitros = listas.get_lista_arbitros()
				for arb in arbitros:
					if arb.arb_nome == results["arbitro"]:
						arbitro = arb
						logging.info('Árbitro detectado')

			if not arbitro:
				logging.info('Árbitro NÃO detectado')
			else:
				output["arbitro"] = arbitro.key().id()
				
			if results.has_key("resultado_clube1"):
				output["resultado_clube1"] = results["resultado_clube1"]
			if results.has_key("resultado_clube2"):	
				output["resultado_clube2"] = results["resultado_clube2"]

			logging.info("Resultados detectados")
				
			jog_clube1 = Jogador.all().filter("jgd_clube_actual = ", clube1)
			jog_clube2 = Jogador.all().filter("jgd_clube_actual = ", clube2)

			remote_jogadores_nome1 = {}
			remote_jogadores_nome2 = {}
			local_jogadores_clube1 = {}
			local_jogadores_clube2 = {}

			logging.info("A obter jogadores do %s na DB" % results["clube1"])
			
			for j in jog_clube1:
				if j.jgd_numero != None and j.jgd_numero > 0:
					local_jogadores_clube1[j.jgd_numero] = j
				else:
					logging.error("Jogador %s do %s não tem número, corrige isso!" % (j, results["clube1"]))

			logging.info("A obter jogadores do %s na DB" % results["clube2"])

			for j in jog_clube2:
				if j.jgd_numero != None and j.jgd_numero > 0:
					local_jogadores_clube2[j.jgd_numero] = j
				else:
					logging.error("Jogador %s do %s não tem número, corrige isso!" % (j, results["clube2"]))	

			logging.info('Índices de jogadores preenchidos.')

			if results.has_key("tacticas_clube1"):
				output["tacticas_clube1"] = re.sub("x","-",results["tacticas_clube1"])
			if results.has_key("tacticas_clube2"):
				output["tacticas_clube2"] = re.sub("x","-",results["tacticas_clube2"])
	
			logging.info('Tácticas preenchidas.')

			# hash now. Use an array so we know the final order 
			output["jogadores_clube1"] = {}
			output["jogadores_clube2"] = {}

			jogadores_clube1_order = []
			jogadores_clube2_order = []


			logging.info("A analisar titulares do %s" % results["clube1"])
			
			# titulares: actualizar índice nome-número remoto, adicionar key a main hash
			for remote_jogador in results["jogadores_titulares_clube1"]:
				remote_jogadores_nome1[remote_jogador["nome"]] = remote_jogador["numero"]
				if local_jogadores_clube1.has_key(remote_jogador["numero"]):
					local_jogador = local_jogadores_clube1[remote_jogador["numero"]]
					output["jogadores_clube1"][local_jogador.key().id()] = {}
					jogadores_clube1_order.append(local_jogador.key().id())
					
				else:
					logging.error("Jogador MaisFutebol %s do %s com número %s não consta no FoiPenalti, corrige isso!" % (remote_jogador["nome"], results["clube1"], remote_jogador["numero"]) )	

			logging.info("A analisar titulares do %s" % results["clube2"])

			for remote_jogador in results["jogadores_titulares_clube2"]:
				remote_jogadores_nome2[remote_jogador["nome"]] = remote_jogador["numero"]
				if local_jogadores_clube2.has_key(remote_jogador["numero"]):
					local_jogador = local_jogadores_clube2[remote_jogador["numero"]]
					output["jogadores_clube2"][local_jogador.key().id()] = {}
					jogadores_clube2_order.append(local_jogador.key().id())
				else:
					logging.error("Jogador MaisFutebol %s do %s com número %s não consta no FoiPenalti, corrige isso!" % (remote_jogador["nome"], results["clube2"], remote_jogador["numero"]) )	

			# suplentes: apenas actualizar índice nome-número remoto

			logging.info("A analisar suplentes do %s" % results["clube1"])

			for remote_jogador in results["jogadores_suplentes_clube1"]:
				remote_jogadores_nome1[remote_jogador["nome"]] = remote_jogador["numero"]

			logging.info("A analisar suplentes do %s" % results["clube2"])
			
			for remote_jogador in results["jogadores_suplentes_clube2"]:
				remote_jogadores_nome2[remote_jogador["nome"]] = remote_jogador["numero"]

			# substituições: usar para recuparar mais 3 jogadores e adicionar a main-hash, alterar minutos de substituição

			logging.info("A analisar substituições do %s" % results["clube1"])

			for remote_substituicao in results["substituicoes_clube1"]:

				remote_jogador_saida_nome = remote_substituicao["jogador_saida"]
				remote_jogador_entrada_nome = remote_substituicao["jogador_entrada"]
				remote_jogador_minuto = remote_substituicao["minuto"]
				
				if local_jogadores_clube1.has_key(remote_jogadores_nome1[remote_jogador_saida_nome]):
					local_jogador_saida = local_jogadores_clube1[remote_jogadores_nome1[remote_jogador_saida_nome]]
					output["jogadores_clube1"][local_jogador_saida.key().id()]["substituicao_saida"] = remote_jogador_minuto
				else:	
					logging.error("Jogador MaisFutebol %s do %s, substituído ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_jogador_saida_nome, results["clube1"], remote_jogador_minuto) )	
					
				if local_jogadores_clube1.has_key(remote_jogadores_nome1[remote_jogador_entrada_nome]):
					local_jogador_entrada = local_jogadores_clube1[remote_jogadores_nome1[remote_jogador_entrada_nome]]
					output["jogadores_clube1"][local_jogador_entrada.key().id()] = {"substituicao_entrada":remote_jogador_minuto}
					jogadores_clube1_order.append(local_jogador_entrada.key().id())
				else:	
					logging.error("Jogador MaisFutebol %s do %s, que entrou ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_jogador_entrada_nome, results["clube1"], remote_jogador_minuto) )	

			logging.info("A analisar substituições do %s" % results["clube2"])

			for remote_substituicao in results["substituicoes_clube2"]:

				remote_jogador_saida_nome = remote_substituicao["jogador_saida"]
				remote_jogador_entrada_nome = remote_substituicao["jogador_entrada"]
				remote_jogador_minuto = remote_substituicao["minuto"]

				if local_jogadores_clube2.has_key(remote_jogadores_nome2[remote_jogador_saida_nome]):
					local_jogador_saida = local_jogadores_clube2[remote_jogadores_nome2[remote_jogador_saida_nome]]
					output["jogadores_clube2"][local_jogador_saida.key().id()]["substituicao_saida"] = remote_jogador_minuto
				else:	
					logging.error("Jogador MaisFutebol %s do %s, substituído ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_jogador_saida_nome, results["clube2"], remote_jogador_minuto) )	
					
				if local_jogadores_clube2.has_key(remote_jogadores_nome2[remote_jogador_entrada_nome]):
					local_jogador_entrada = local_jogadores_clube2[remote_jogadores_nome2[remote_jogador_entrada_nome]]
					output["jogadores_clube2"][local_jogador_entrada.key().id()] = {"substituicao_entrada":remote_jogador_minuto}
					jogadores_clube2_order.append(local_jogador_entrada.key().id())
				else:	
					logging.error("Jogador MaisFutebol %s do %s, que entrou ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_jogador_entrada_nome, results["clube2"], remote_jogador_minuto) )	

			# CARTOES

			logging.info("A analisar cartões do %s" % results["clube1"])

			for remote_cartoes in results["cartoes_clube1"]:
				remote_cartao_minuto = remote_cartoes["minuto"]
				remote_cartao_tipo = remote_cartoes["cartao"]
				remote_cartao_jogador = remote_cartoes["jogador"]

				if local_jogadores_clube1.has_key(remote_jogadores_nome1[remote_cartao_jogador]):
					local_jogador = local_jogadores_clube1[remote_jogadores_nome1[remote_cartao_jogador]]
					output["jogadores_clube1"][local_jogador.key().id()][remote_cartao_tipo] = remote_cartao_minuto
				else:	
					logging.error("Jogador MaisFutebol %s do %s, que viu cartão ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_cartao_jogador, results["clube1"], remote_cartao_minuto) )	

			for remote_cartoes in results["cartoes_clube2"]:
				remote_cartao_minuto = remote_cartoes["minuto"]
				remote_cartao_tipo = remote_cartoes["cartao"]
				remote_cartao_jogador = remote_cartoes["jogador"]

				if local_jogadores_clube2.has_key(remote_jogadores_nome2[remote_cartao_jogador]):
					local_jogador = local_jogadores_clube2[remote_jogadores_nome2[remote_cartao_jogador]]
					output["jogadores_clube2"][local_jogador.key().id()][remote_cartao_tipo] = remote_cartao_minuto
				else:	
					logging.error("Jogador MaisFutebol %s do %s, que viu cartão ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_cartao_jogador, results["clube2"], remote_cartao_minuto) )	

			# GOLOS

			logging.info("A analisar golos dos jogadores")

			for remote_golos in results["golos"]:
				remote_golo_minuto = remote_golos["minuto"]
				remote_golo_tipo = remote_golos["tipo"]
				remote_golo_jogador = remote_golos["jogador"]

				added = False
				
				if remote_jogadores_nome1.has_key(remote_golo_jogador) and local_jogadores_clube1.has_key(remote_jogadores_nome1[remote_golo_jogador]):

					local_jogador = local_jogadores_clube1[remote_jogadores_nome1[remote_golo_jogador]]
					
					if not output["jogadores_clube1"].has_key(local_jogador.key().id()):
							output["jogadores_clube1"][local_jogador.key().id()] = {}
					if not output["jogadores_clube1"][local_jogador.key().id()].has_key("golos"):
						output["jogadores_clube1"][local_jogador.key().id()]["golos"] = []

					output["jogadores_clube1"][local_jogador.key().id()]["golos"].append({
						"minuto":remote_golo_minuto,
						"tipo":remote_golo_tipo
					})
					added = True

				if remote_jogadores_nome2.has_key(remote_golo_jogador) and local_jogadores_clube2.has_key(remote_jogadores_nome2[remote_golo_jogador]):

					local_jogador = local_jogadores_clube2[remote_jogadores_nome2[remote_golo_jogador]]

					if not output["jogadores_clube2"].has_key(local_jogador.key().id()):
							output["jogadores_clube2"][local_jogador.key().id()] = {}

					if not output["jogadores_clube2"][local_jogador.key().id()].has_key("golos"):
						output["jogadores_clube2"][local_jogador.key().id()]["golos"] = []

					output["jogadores_clube2"][local_jogador.key().id()]["golos"].append({
						"minuto":remote_golo_minuto,
						"tipo":remote_golo_tipo
					})					
					added = True
				
				if not added:
					logging.error("Jogador MaisFutebol %s, que marcou golo ao minuto %s, não consta no FoiPenalti, corrige isso!" % (remote_golo_jogador, remote_golo_minuto) )	
		
			output_jogadores_1 = []
			output_jogadores_2 = []
			for idx, val in enumerate(jogadores_clube1_order):
				output_jogadores_1.append({"id":val, "info":output["jogadores_clube1"][val]})
			for idx, val in enumerate(jogadores_clube2_order):
				output_jogadores_2.append({"id":val, "info":output["jogadores_clube2"][val]})
			
			output["jogadores_clube1"] = output_jogadores_1
			output["jogadores_clube2"] = output_jogadores_2
			
			return self.response.out.write(simplejson.dumps({"status":"OK", "message":output}))
