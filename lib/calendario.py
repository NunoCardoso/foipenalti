# -*- coding: utf-8 -*-

import logging
import re
import config 
import datetime
import sys

from classes import *

def url_jornada(jornada):
		return u"<A HREF='/detalhe_jornada?id=%s'>%s %s</A>" % (str(jornada.key().id()), jornada.jor_competicao.cmp_nome_completo, jornada.jor_nome_completo)

def url_jogo(jogo):
		return "<A HREF='/detalhe_jogo?id=%s'>%s</A>" % (str(jogo.key().id()), jogo.printjogo())
		
def gera_calendario_epoca(epoca, jogos):
		# como isto é para Javascript, de notar que os meses começam em 0 e acabam em 11!
		today = datetime.date.today()
		today_month = today.month - 1
		today_year = today.year
		
		calendario_epoca = []
		jogos_calendario = {}
		
		start_month=epoca.epo_data_inicio.month
		end_months=(epoca.epo_data_fim.year-epoca.epo_data_inicio.year)*12 + epoca.epo_data_fim.month+1
		calendario_epoca=[{'mes':mn-1,'ano':yr}  for (yr, mn) in (
          ((m - 1) / 12 + epoca.epo_data_inicio.year, (m - 1) % 12 + 1) for m in range(start_month, end_months)
      )]

#		logging.info(calendario_epoca)
		
		# vamos organizar por meses
		for j in jogos:
			if not jogos_calendario.has_key(j.jog_data.year):
				jogos_calendario[j.jog_data.year] = {}
			if not jogos_calendario[j.jog_data.year].has_key(j.jog_data.month - 1):
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1] = {}
			if not jogos_calendario[j.jog_data.year][j.jog_data.month - 1].has_key(j.jog_data.day):
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day] = {}
			
			# labels de jornadas
			if not jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day].has_key("jornadas"):
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jornadas"] = []
			if not url_jornada(j.jog_jornada) in jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jornadas"]:
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jornadas"].append(url_jornada(j.jog_jornada))
				
			# labels de jogos 
			if not jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day].has_key("jogos"):
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jogos"] = []
			jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jogos"].append(url_jogo(j))
		
		return calendario_epoca, jogos_calendario