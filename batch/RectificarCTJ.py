# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime

competicao = Competicao.all().filter("cmp_nome = ","2011/2012:Liga").get()
epoca = competicao.cmp_epoca
epocas = []
epocas.append(epoca.key()) 

print "competi��o: %s" % competicao

for cjc in competicao.cmp_clubes:
	print "clube: %s" % cjc.cjc_clube
	jogadores = Jogador.all().filter("jgd_clube_actual = ", cjc.cjc_clube)
	for obj in jogadores:

		# 2. ir � BD de CTJ para este jogador
		ctjs = obj.jgd_clubes.filter("ctj_epocas in ", epocas).fetch(1000)
		
		# 3. � estranho n�o ter CTJ, mas se n�o tiver, crio. 
		if not ctjs:
			print "Jogador %s n�o tem ctj para clube %s e �poca %s, a criar um com n�mero %s" % (obj, cjc.cjc_clube, epoca, obj.jgd_numero)
			new_obj = ClubeTemJogador(
				ctj_jogador = obj,
				ctj_clube = cjc.cjc_clube, 
				ctj_numero = obj.jgd_numero,
				ctj_epocas = epocas
			)
			db.put(new_obj)
		else:
			if cjc.cjc_clube.clu_nome != "unknown":

				ctj_deste_clube = None
				for idx, val in enumerate(ctjs):
					if (ctjs[idx].ctj_clube == cjc.cjc_clube):
						ctj_deste_clube = ctjs[idx]
				
				if ctj_deste_clube != None:
					print "Encontrei um CTJ para esta �poca: %s. A ver se vamos editar. " % ctj_deste_clube
					if ctj_deste_clube.ctj_numero == obj.jgd_numero:
						print "O CTJ j� tem o n�mero que o jogador tem actualmente, skipping"
					else:
						print "O CTJ n�o tem o n�mero que o jogador tem actualmente, updating"
						ctj_deste_clube.ctj_numero = obj.jgd_numero
						db.put(ctj_deste_clube)
				else:
					print "N�o encontrei um CTJ para esta �poca. A criar novo. " 
					new_obj = ClubeTemJogador(
						ctj_jogador = obj,
						ctj_clube = cjc.cjc_clube, 
						ctj_numero = obj.jgd_numero,
						ctj_epocas = epocas
					)
					db.put(new_obj)
