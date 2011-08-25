# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import re
competicao = Competicao.all().filter("cmp_nome = ","2010/2011:Liga")
for jornada in competicao.cmp_jornadas:
	jornada.jor_nome_completo = jornada.jor_nome_completo.replace("a ", "ª ")
	jornada.put()
	logging.info(jornada)


	
