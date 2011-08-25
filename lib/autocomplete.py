# -*- coding: utf-8 -*-

# no_memcache, cache_Dados e cache_html

import os
import datetime
import logging
import re
import config 

from classes import *
from lib.myhandler import MyHandler

class NomeJogador(MyHandler):

	def get(self):
		
		q = self.request.get("q")
		q = q.capitalize()
		#logging.info("Got q "+q)
		jogadores = db.GqlQuery("SELECT * FROM Jogador WHERE jgd_nome >= :1 AND jgd_nome < :2", q, u""+unicode(q) + u"\ufffd")
#		logging.info("jogadores  "+str(jogadores.count()))

		stringlist = []
		for jogador in jogadores:
			stringlist.append(str(jogador.key().id())+"|"+jogador.jgd_nome)
			
		self.response.out.write("\n".join(stringlist))

class NomeClube(MyHandler):

	def get(self):
		
		q = self.request.get("q")
		q = q.capitalize()
		#logging.info("Got q "+q)
		clubes = db.GqlQuery("SELECT * FROM Clube WHERE clu_nome_curto >= :1 AND clu_nome_curto < :2", q, u""+unicode(q) + u"\ufffd")

		stringlist = []
		for clube in clubes:
			stringlist.append(str(clube.key().id())+"|"+clube.clu_nome_curto)
			
		self.response.out.write("\n".join(stringlist))

class NomeArbitro(MyHandler):

	def get(self):
		
		q = self.request.get("q")
		q = q.capitalize()
		#logging.info("Got q "+q)
		arbitros = db.GqlQuery("SELECT * FROM Arbitro WHERE arb_nome >= :1 AND arb_nome < :2", q, u""+unicode(q) + u"\ufffd")

		stringlist = []
		for arbitro in arbitros:
			stringlist.append(str(arbitro.key().id())+"|"+arbitro.arb_nome)
			
		self.response.out.write("\n".join(stringlist))


class CompeticoesDeEpoca(MyHandler):

	def get(self):
		
		q = self.request.get("q")
		q = q.capitalize()
		logging.info("Got q "+q)
		competicoes = db.GqlQuery("SELECT * FROM Competicao WHERE cmp_epoca = :1", q)

		stringlist = []
		for competicao in competicoes:
			stringlist.append(str(competicao.key().id())+"|"+competicao.cmp_nome_completo)
			
		self.response.out.write("\n".join(stringlist))