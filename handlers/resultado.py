# -*- coding: utf-8 -*-

from google.appengine.api import memcache

import os
import datetime
import logging
import re
import config 

from classes import *
from lib.myhandler import MyHandler

class Resultado(MyHandler):

	def get(self):
 # Recebe um click dos resultados da pesquisa, e redirecciona para o detalhe_X:
 # resultado?obj=jogo&panel=[pesquisa|top]&total=20&nr=15&click=2&from=procurar_jogo&to=detalhe_jogo&id=X
 # obj: tipo de objecto
 # panel: caso haja diferentes painéis (pesquisa, top vistos, top recentes)
 # total: total de elementos que correspondem aos critérios da pesquisa: 
 # nr: nº elementos por cada página de resultados 
 # click: qual o elemento que foi clicado
 # from/to: de que servlet, para que servlet
 # id: id do objecto a usar
		# 
		# obj = self.request.get("obj")
		# panel = self.request.get("panel")
		# total = self.request.get("total")
		# nr = self.request.get("nr")
		# click = self.request.get("click")
		# from_ = self.request.get("from")
		to = self.request.get("to")
		id = self.request.get("id")
	
		url = to+"?id="+id
		return self.redirect(str(url))
