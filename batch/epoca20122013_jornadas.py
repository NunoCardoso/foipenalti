# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
epoca = Epoca.all().filter("epo_nome = ", "2012/2013").get()
epoant = Epoca.all().filter("epo_nome = ", "2011/2012").get()
date = datetime.datetime.now()

cmp1 = Competicao.all().filter("cmp_nome = ","2011/2012:SuperTaca").get()
j1 = Jornada(\
		jor_numero_visitas = 0,\
        jor_ultima_alteracao = date,\
        jor_nome = "2011/2012:SuperTaca:final",\
        jor_data = datetime.date(2012, 8, 11),\
        jor_nome_curto = "final",\
        jor_nome_completo = "Final",\
        jor_ordem = 1,\
        jor_competicao = cmp1,\
        jor_epoca = epoant,\
        jor_link_zz = "http://www.foipenalit.com"\
)
j1.put()

c = Competicao.all().filter("cmp_nome = ","2012/2013:Liga").get()


datas = [\
(2012,8,17),\
(2012,8,26),\
(2012,9,2),\
(2012,9,23),\
(2012,9,30),\
(2012,10,7),\
(2012,10,28),\
(2012,11,4),\
(2012,11,11),\
(2012,11,25),\

(2012,12,9),\
(2012,12,16),\
(2013,1,6),\
(2013,1,13),\
(2013,1,20),\
(2013,1,27),\
(2013,2,3),\
(2013,2,10),\
(2013,2,17),\
(2013,2,24),\

(2013,3,3),\
(2013,3,10),\
(2013,3,17),\
(2013,3,30),\
(2013,4,7),\
(2013,4,21),\
(2013,4,28),\
(2013,4,5),\
(2013,4,12),\
(2013,4,19)\
]

for idx, val in enumerate(datas):
	j1 = Jornada(\
	        jor_numero_visitas = 0,\
	        jor_ultima_alteracao = date,\
	        jor_nome = "2012/2013:Liga:" + str(idx + 1),\
	        jor_data = datetime.date(val[0], val[1], val[2]),\
	        jor_nome_curto = ""+str(idx + 1),\
	        jor_nome_completo = str(idx + 1)+"a jornada",\
	        jor_ordem = (idx + 1),\
	        jor_competicao = c,\
	        jor_epoca = epoca,\
	        jor_link_zz = "http://www.foipenali.com"\
	)
	j1.put()