# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
jornada = Jornada.all().filter("jor_nome = ", "2010/2011:TacaLiga:2f1j").get()
jogos = Jogo.all().filter("jog_jornada = ", jornada)
for j in jogos:
	for l in j.jog_lances:
		l.lan_nome = jornada.jor_nome+":"+j.jog_clube1.clu_nome+":"+j.jog_clube2.clu_nome+":"+str(l.lan_numero)
		l.put()

	
