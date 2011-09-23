# -*- coding: utf-8 -*-

#### VERSAO 5: ENCERRADO ####

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 
import urllib

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler


class Delete(MyHandler):
	
	def get(self, objname):

		id = int(self.request.get('id'))

		referer = urllib.unquote_plus(self.request.get('referrer'))   
		if not referer:
			referer = os.environ['HTTP_REFERER'] 
		flash_messages = []

#############
### CLUBE ###
#############

		if objname == "clube":
			obj = Clube.get_by_id(id)

			for ctj in obj.clu_jogadores:
				flash_messages.append(u"%s %s apagada." % (ctj.kind(), ctj.__str__().decode("utf-8","replace")))
				memcache.delete(str(ctj.key().id()), namespace="clube_tem_jogador")
				ctj.delete()

			for cjc in obj.clu_competicoes:
				flash_messages.append(u"%s %s apagada." % (cjc.kind(), cjc.__str__().decode("utf-8","replace")))
				memcache.delete(str(cjc.key().id()), namespace="clube_joga_competicao")
				cjc.delete()

		elif objname == "jogador":
			obj = Jogador.get_by_id(id)
		elif objname == "epoca":
			obj = Epoca.get_by_id(id)
		elif objname == "competicao":
			obj = Competicao.get_by_id(id)

############
### JOGO ###
############

		elif objname == "jogo":
			obj = Jogo.get_by_id(id)

			for lance in obj.jog_lances:
				flash_messages.append(u"%s %s apagada." % (lance.kind(), lance.__str__().decode("utf-8","replace")))
				memcache.delete(str(lance.key().id()), namespace="lance")
				lance.delete()
			
			for jjj in obj.jog_jogadores:
				flash_messages.append(u"%s %s apagada," % (jjj.kind(), jjj.__str__().decode("utf-8","replace")))
				memcache.delete(str(jjj.key().id()), namespace="jogador_joga_jogo")
				jjj.delete()
					
###############
### ARBITRO ###
###############

		elif objname == "arbitro":
			obj = Arbitro.get_by_id(id)
			
##################
### COMENTADOR ###
##################
			
		elif objname == "comentador":
			obj = Comentador.get_by_id(id)
			for ccl in obj.com_lances:
				flash_messages.append(u"%s %s apagada." % (ccl.kind(), ccl.__str__().decode("utf-8","replace")))
				memcache.delete(str(ccl.key().id()), namespace="comentador_comenta_lance")
				ccl.delete()
			
#############
### FONTE ###
#############
	
		elif objname == "fonte":
			obj = Fonte.get_by_id(id)

###############
### JORNADA ###
###############

		elif objname == "jornada":
			obj = Jornada.get_by_id(id)

			for jogo in obj.jor_jogos:
				flash_messages.append(u"%s %s apagada." % (jogo.kind(), jogo.__str__().decode("utf-8","replace")))
				memcache.delete(str(jogo.key().id()), namespace="jogo")
				jogo.delete()

#############
### LANCE ###
#############
				
		elif objname == "lance":
			obj = Lance.get_by_id(id)

			for jel in obj.lan_jogadores:
				flash_messages.append(u"%s apagada." % jel.kind()) #, jel.__str__().decode("utf-8","replace")))
				memcache.delete(str(jel.key().id()), namespace="jogador_em_lance")
				jel.delete()
				
			for ccl in obj.lan_comentadores:
				flash_messages.append(u"%s apagada." % ccl.kind()) #, ccl.__str__().decode("utf-8","replace")))
				memcache.delete(str(ccl.key().id()), namespace="comentador_comenta_lance")
				ccl.delete()

###############
### JOGADOR ###
###############

		elif objname == "jogador":
			obj = Jogador.get_by_id(id)

			for jjj in obj.jgd_jogos:
				flash_messages.append(u"%s %s apagada." % (jjj.kind(), jjj.__str__().decode("utf-8","replace")))
				memcache.delete(str(jjj.key().id()), namespace="jogador_joga_jogo")
				jjj.delete()
				
			for jel in obj.jgd_lances:
				flash_messages.append(u"%s %s apagada." % (jel.kind(), jel.__str__().decode("utf-8","replace")))
				memcache.delete(str(jel.key().id()), namespace="jogador_em_lance")
				jel.delete()

#############
### EPOCA ###
#############


##############
# COMPETICAO #
##############

# EPOCA e COMPETICAO tem o mesmo problema de JORNADA; esta pode apagar os jogos, 
# mas não apaga os lances, e os jogador_em_lance, comentador_em_lance, etc. 
# por outras palavras, apagar uma época pressupõe apagar 4 competições, 50 jornadas, 200 jogos, 1000 lances, sem falar dos jjj, ctj, jel, etc.

# Por outras palavras, é melhor nem equacionar apagar estes, porque não há necessidade

		elif objname == "clube_tem_jogador":
			obj = ClubeTemJogador.get_by_id(id)
		elif objname == "clube_joga_competicao":
			obj = ClubeJogaCompeticao.get_by_id(id)
		elif objname == "jogador_joga_jogo":
			obj = JogadorJogaJogo.get_by_id(id)
		elif objname == "comentador_comenta_lance":
			obj = ComentadorComentaLance.get_by_id(id)
		elif objname == "jogador_em_lance":
			obj = JogadorEmLance.get_by_id(id)
		
		elif objname == "acumulador_jornada":
			obj = AcumuladorJornada.get_by_id(id)
		elif objname == "acumulador_competicao":
			obj = AcumuladorCompeticao.get_by_id(id)
		elif objname == "acumulador_epoca":
			obj = AcumuladorEpoca.get_by_id(id)

		if obj:
			flash_messages.append(
				u"%s %s apagada." % (obj.kind(), obj.__str__().decode("utf-8","replace"))
				)
			memcache.delete(str(obj.key().id()), namespace=objname)
			obj.delete()
			
		new_sid = self.generate_sid()
		memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
		self.add_sid_to_cookie(new_sid)
		self.redirect(referer)