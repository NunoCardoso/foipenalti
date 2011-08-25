# atribuir aos jogos a data das jornadas
# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
competicao = Competicao.all().filter("cmp_nome = ", "2011/2012:Liga").get()
jornadas = competicao.cmp_jornadas
for jor in jornadas:
	jogos = jor.jor_jogos
	for jog in jogos:
		jog.jog_data = datetime.datetime.combine(jor.jor_data, datetime.time())
		jog.put()
		
