# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
epoca = Epoca.all().filter("epo_nome = ", "2012/2013").get()
epoant = Epoca.all().filter("epo_nome = ", "2011/2012").get()
date = datetime.datetime.now()

c = Competicao.all().filter("cmp_nome = ","2012/2013:Liga").get()

porto = Clube.all().filter("clu_nome = ", "Porto").get()
academica = Clube.all().filter("clu_nome = ", "Academica").get()
olhanense = Clube.all().filter("clu_nome = ", "Olhanense").get()
estoril = Clube.all().filter("clu_nome = ", "Estoril").get() 
rioave = Clube.all().filter("clu_nome = ", "RioAve").get()
maritimo = Clube.all().filter("clu_nome = ", "Maritimo").get() 
benfica = Clube.all().filter("clu_nome = ", "Benfica").get()
braga = Clube.all().filter("clu_nome = ", "Braga").get() 
nacional = Clube.all().filter("clu_nome = ", "Nacional").get()
setubal = Clube.all().filter("clu_nome = ", "Setubal").get() 
pacos = Clube.all().filter("clu_nome = ", "PacosFerreira").get() 
moreirense = Clube.all().filter("clu_nome = ", "Moreirense").get() 
gilvicente = Clube.all().filter("clu_nome = ", "GilVicente").get()
guimaraes = Clube.all().filter("clu_nome = ", "Guimaraes").get()
sporting = Clube.all().filter("clu_nome = ", "Sporting").get()
beiramar = Clube.all().filter("clu_nome = ", "BeiraMar").get()

jogos = [\
	[],\
	[ #1\
	(2012, 17, 8, 20, 15,  olhanense,  estoril),\
	(2012, 18, 8, 18, 15,  rioave, maritimo),\
	(2012, 18, 8, 20, 15,  benfica, braga),\
	(2012, 19, 8, 16, 0,  nacional, setubal),\
	(2012, 19, 8, 18, 0,  pacos, moreirense),\
	(2012, 19, 8, 18, 15,  gilvicente, porto),\
	(2012, 19, 8, 20, 30,  guimaraes, sporting),\
	(2012, 20, 8, 20, 15,  beiramar, academica)\
	],\
	[ #2\
	(2012, 26, 8, 0, 0,  setubal , benfica),\
	(2012, 26, 8, 0, 0,  maritimo , gilvicente),\
	(2012, 26, 8, 0, 0,  sporting , rioave),\
	(2012, 26, 8, 0, 0,  estoril , pacos),\
	(2012, 26, 8, 0, 0,  porto , guimaraes),\
	(2012, 26, 8, 0, 0,  academica , olhanense),\
	(2012, 26, 8, 0, 0,  braga , beiramar),\
	(2012, 26, 8, 0, 0,  moreirense , nacional)\
	],\
	[ #3\
	(2012, 2, 9, 0, 0,  rioave , academica),\
	(2012, 2, 9, 0, 0,  maritimo , sporting),\
	(2012, 2, 9, 0, 0,  benfica , nacional),\
	(2012, 2, 9, 0, 0,  pacos , braga),\
	(2012, 2, 9, 0, 0,  beiramar , moreirense),\
	(2012, 2, 9, 0, 0,  olhanense , porto),\
	(2012, 2, 9, 0, 0,  guimaraes , estoril),\
	(2012, 2, 9, 0, 0,  gilvicente , setubal)\
	],\
	[ #4\
	(2012, 23, 9, 0, 0,  setubal , olhanense),\
	(2012, 23, 9, 0, 0,  nacional , pacos),\
	(2012, 23, 9, 0, 0,  sporting , gilvicente),\
	(2012, 23, 9, 0, 0,  estoril , maritimo),\
	(2012, 23, 9, 0, 0,  porto , beiramar),\
	(2012, 23, 9, 0, 0,  academica , benfica),\
	(2012, 23, 9, 0, 0,  braga , rioave),\
	(2012, 23, 9, 0, 0,  moreirense , guimaraes)\
	],\
	[ #5\
	(2012, 30, 9, 0, 0,  maritimo , academica),\
	(2012, 30, 9, 0, 0,  gilvicente , moreirense),\
	(2012, 30, 9, 0, 0,  rioave , porto),\
	(2012, 30, 9, 0, 0,  sporting , estoril),\
	(2012, 30, 9, 0, 0,  pacos , benfica),\
	(2012, 30, 9, 0, 0,  beiramar , setubal),\
	(2012, 30, 9, 0, 0,  olhanense , nacional),\
	(2012, 30, 9, 0, 0,  guimaraes , braga)\
	],\
	[ #6\
	(2012, 7, 10, 0, 0,  setubal , pacos),\
	(2012, 7, 10, 0, 0,  nacional , gilvicente),\
	(2012, 7, 10, 0, 0,  benfica , beiramar),\
	(2012, 7, 10, 0, 0,  estoril , rioave),\
	(2012, 7, 10, 0, 0,  porto , sporting),\
	(2012, 7, 10, 0, 0,  academica , guimaraes),\
	(2012, 7, 10, 0, 0,  braga , olhanense),\
	(2012, 7, 10, 0, 0,  moreirense , maritimo)\
	],\
	[ #7\
	(2012, 28, 10, 0, 0,  sporting , academica),\
	(2012, 28, 10, 0, 0,  rioave , nacional),\
	(2012, 28, 10, 0, 0,  maritimo , braga),\
	(2012, 28, 10, 0, 0,  estoril , porto),\
	(2012, 28, 10, 0, 0,  beiramar , pacos),\
	(2012, 28, 10, 0, 0,  olhanense , moreirense),\
	(2012, 28, 10, 0, 0,  guimaraes , setubal),\
	(2012, 28, 10, 0, 0,  gilvicente , benfica)\
	],\
	[ #8\
	(2012, 4, 11, 0, 0,  setubal , sporting),\
	(2012, 4, 11, 0, 0,  pacos , olhanense),\
	(2012, 4, 11, 0, 0,  nacional , beiramar),\
	(2012, 4, 11, 0, 0,  benfica , guimaraes),\
	(2012, 4, 11, 0, 0,  porto , maritimo),\
	(2012, 4, 11, 0, 0,  academica , estoril),\
	(2012, 4, 11, 0, 0,  braga , gilvicente),\
	(2012, 4, 11, 0, 0,  moreirense , rioave)\
	],\
	[ #9\
	(2012, 11, 11, 0, 0,  maritimo , setubal),\
	(2012, 11, 11, 0, 0,  sporting , braga),\
	(2012, 11, 11, 0, 0,  rioave , benfica),\
	(2012, 11, 11, 0, 0,  estoril , moreirense),\
	(2012, 11, 11, 0, 0,  porto , academica),\
	(2012, 11, 11, 0, 0,  olhanense , beiramar),\
	(2012, 11, 11, 0, 0,  guimaraes , nacional),\
	(2012, 11, 11, 0, 0,  gilvicente , pacos)\
	],\
	[ #10\
	(2012, 25, 11, 0, 0,  setubal , rioave),\
	(2012, 25, 11, 0, 0,  nacional , estoril),\
	(2012, 25, 11, 0, 0,  benfica , olhanense),\
	(2012, 25, 11, 0, 0,  pacos , maritimo),\
	(2012, 25, 11, 0, 0,  beiramar , guimaraes),\
	(2012, 25, 11, 0, 0,  academica , gilvicente),\
	(2012, 25, 11, 0, 0,  braga , porto),\
	(2012, 25, 11, 0, 0,  moreirense , sporting)\
	],\
	[ #11\
	(2012, 9, 12, 0, 0,  gilvicente , beiramar),\
	(2012, 9, 12, 0, 0,  rioave , pacos),\
	(2012, 9, 12, 0, 0,  maritimo , nacional),\
	(2012, 9, 12, 0, 0,  sporting , benfica),\
	(2012, 9, 12, 0, 0,  estoril , setubal),\
	(2012, 9, 12, 0, 0,  porto , moreirense),\
	(2012, 9, 12, 0, 0,  academica , braga),\
	(2012, 9, 12, 0, 0,  guimaraes , olhanense)\
	],\
	[ #12\
	(2012, 16, 12, 0, 0,  setubal , porto),\
	(2012, 16, 12, 0, 0,  nacional , sporting),\
	(2012, 16, 12, 0, 0,  benfica , maritimo),\
	(2012, 16, 12, 0, 0,  pacos , guimaraes),\
	(2012, 16, 12, 0, 0,  beiramar , rioave),\
	(2012, 16, 12, 0, 0,  olhanense , gilvicente),\
	(2012, 16, 12, 0, 0,  braga , estoril),\
	(2012, 16, 12, 0, 0,  moreirense , academica)\
	],\
	[ #13\
	(2012, 6, 1, 0, 0,  rioave , olhanense),\
	(2012, 6, 1, 0, 0,  maritimo , beiramar),\
	(2012, 6, 1, 0, 0,  sporting , pacos),\
	(2012, 6, 1, 0, 0,  estoril , benfica),\
	(2012, 6, 1, 0, 0,  porto , nacional),\
	(2012, 6, 1, 0, 0,  academica , setubal),\
	(2012, 6, 1, 0, 0,  braga , moreirense),\
	(2012, 6, 1, 0, 0,  gilvicente , guimaraes)\
	],\
	[ #14\
	(2012, 13, 1, 0, 0,  setubal , moreirense),\
	(2012, 13, 1, 0, 0,  nacional , braga),\
	(2012, 13, 1, 0, 0,  benfica , porto),\
	(2012, 13, 1, 0, 0,  pacos , academica),\
	(2012, 13, 1, 0, 0,  beiramar , estoril),\
	(2012, 13, 1, 0, 0,  olhanense , sporting),\
	(2012, 13, 1, 0, 0,  guimaraes , maritimo),\
	(2012, 13, 1, 0, 0,  gilvicente , rioave)\
	],\
	[ #15\
	(2012, 20, 1, 0, 0,  rioave , guimaraes),\
	(2012, 20, 1, 0, 0,  maritimo , olhanense),\
	(2012, 20, 1, 0, 0,  sporting , beiramar),\
	(2012, 20, 1, 0, 0,  estoril , gilvicente),\
	(2012, 20, 1, 0, 0,  porto , pacos),\
	(2012, 20, 1, 0, 0,  academica , nacional),\
	(2012, 20, 1, 0, 0,  braga , setubal),\
	(2012, 20, 1, 0, 0,  moreirense , benfica)\
	],\
	[ #16\
	(2012, 27, 1, 0, 0,  maritimo , rioave),\
	(2012, 27, 1, 0, 0,  setubal , nacional),\
	(2012, 27, 1, 0, 0,  braga , benfica),\
	(2012, 27, 1, 0, 0,  moreirense , pacos),\
	(2012, 27, 1, 0, 0,  academica , beiramar),\
	(2012, 27, 1, 0, 0,  estoril , olhanense),\
	(2012, 27, 1, 0, 0,  sporting , guimaraes),\
	(2012, 27, 1, 0, 0,  porto , gilvicente)\
	],\
	[ #17\
	(2012, 3, 2, 0, 0,  benfica , setubal),\
	(2012, 3, 2, 0, 0,  gilvicente , maritimo),\
	(2012, 3, 2, 0, 0,  rioave , sporting),\
	(2012, 3, 2, 0, 0,  pacos , estoril),\
	(2012, 3, 2, 0, 0,  guimaraes , porto),\
	(2012, 3, 2, 0, 0,  olhanense , academica),\
	(2012, 3, 2, 0, 0,  beiramar , braga),\
	(2012, 3, 2, 0, 0,  nacional , moreirense)\
	],\
	[ #18\
	(2012, 10, 2, 0, 0,  academica , rioave),\
	(2012, 10, 2, 0, 0,  sporting , maritimo),\
	(2012, 10, 2, 0, 0,  nacional , benfica),\
	(2012, 10, 2, 0, 0,  braga , pacos),\
	(2012, 10, 2, 0, 0,  moreirense , beiramar),\
	(2012, 10, 2, 0, 0,  porto , olhanense),\
	(2012, 10, 2, 0, 0,  estoril , guimaraes),\
	(2012, 10, 2, 0, 0,  setubal , gilvicente)\
	],\
	[ #19\
	(2012, 17, 2, 0, 0,  olhanense , setubal),\
	(2012, 17, 2, 0, 0,  pacos , nacional),\
	(2012, 17, 2, 0, 0,  gilvicente , sporting),\
	(2012, 17, 2, 0, 0,  maritimo , estoril),\
	(2012, 17, 2, 0, 0,  beiramar , porto),\
	(2012, 17, 2, 0, 0,  benfica , academica),\
	(2012, 17, 2, 0, 0,  rioave , braga),\
	(2012, 17, 2, 0, 0,  guimaraes , moreirense)\
	],\
	[ #20\
	(2012, 24, 2, 0, 0,  porto , rioave),\
	(2012, 24, 2, 0, 0,  academica , maritimo),\
	(2012, 24, 2, 0, 0,  estoril , sporting),\
	(2012, 24, 2, 0, 0,  benfica , pacos),\
	(2012, 24, 2, 0, 0,  setubal , beiramar),\
	(2012, 24, 2, 0, 0,  nacional , olhanense),\
	(2012, 24, 2, 0, 0,  braga , guimaraes),\
	(2012, 24, 2, 0, 0,  moreirense , gilvicente)\
	],\
	[ #21\
	(2012, 3, 3, 0, 0,  pacos , setubal),\
	(2012, 3, 3, 0, 0,  gilvicente , nacional),\
	(2012, 3, 3, 0, 0,  beiramar , benfica),\
	(2012, 3, 3, 0, 0,  rioave , estoril),\
	(2012, 3, 3, 0, 0,  sporting , porto),\
	(2012, 3, 3, 0, 0,  guimaraes , academica),\
	(2012, 3, 3, 0, 0,  olhanense , braga),\
	(2012, 3, 3, 0, 0,  maritimo , moreirense)\
	],\
	[ #22\
	(2012, 10, 3, 0, 0,  nacional , rioave),\
	(2012, 10, 3, 0, 0,  benfica , gilvicente),\
	(2012, 10, 3, 0, 0,  setubal , guimaraes),\
	(2012, 10, 3, 0, 0,  moreirense , olhanense),\
	(2012, 10, 3, 0, 0,  pacos , beiramar),\
	(2012, 10, 3, 0, 0,  porto , estoril),\
	(2012, 10, 3, 0, 0,  academica , sporting),\
	(2012, 10, 3, 0, 0,  braga , maritimo)\
	],\
	[ #23\
	(2012, 17, 3, 0, 0,  rioave , moreirense),\
	(2012, 17, 3, 0, 0,  gilvicente , braga),\
	(2012, 17, 3, 0, 0,  estoril , academica),\
	(2012, 17, 3, 0, 0,  maritimo , porto),\
	(2012, 17, 3, 0, 0,  olhanense , pacos),\
	(2012, 17, 3, 0, 0,  guimaraes , benfica),\
	(2012, 17, 3, 0, 0,  beiramar , nacional),\
	(2012, 17, 3, 0, 0,  sporting , setubal)\
	],\
	[ #24\
	(2012, 30, 3, 0, 0,  pacos , gilvicente),\
	(2012, 30, 3, 0, 0,  nacional , guimaraes),\
	(2012, 30, 3, 0, 0,  beiramar , olhanense),\
	(2012, 30, 3, 0, 0,  moreirense , estoril),\
	(2012, 30, 3, 0, 0,  braga , sporting),\
	(2012, 30, 3, 0, 0,  setubal , maritimo),\
	(2012, 30, 3, 0, 0,  benfica , rioave),\
	(2012, 30, 3, 0, 0,  academica , porto)\
	],\
	[ #25\
	(2012, 7, 4, 0, 0,  sporting , moreirense),\
	(2012, 7, 4, 0, 0,  porto , braga),\
	(2012, 7, 4, 0, 0,  gilvicente , academica),\
	(2012, 7, 4, 0, 0,  maritimo , pacos),\
	(2012, 7, 4, 0, 0,  olhanense , benfica),\
	(2012, 7, 4, 0, 0,  rioave , setubal),\
	(2012, 7, 4, 0, 0,  estoril , nacional),\
	(2012, 7, 4, 0, 0,  guimaraes , beiramar)\
	],\
	[ #26\
	(2012, 21, 4, 0, 0,  beiramar , gilvicente),\
	(2012, 21, 4, 0, 0,  olhanense , guimaraes),\
	(2012, 21, 4, 0, 0,  braga , academica),\
	(2012, 21, 4, 0, 0,  moreirense , porto),\
	(2012, 21, 4, 0, 0,  setubal , estoril),\
	(2012, 21, 4, 0, 0,  benfica , sporting),\
	(2012, 21, 4, 0, 0,  nacional , maritimo),\
	(2012, 21, 4, 0, 0,  pacos , rioave)\
	],\
	[ #27\
	(2012, 28, 4, 0, 0,  academica , moreirense),\
	(2012, 28, 4, 0, 0,  estoril , braga),\
	(2012, 28, 4, 0, 0,  gilvicente , olhanense),\
	(2012, 28, 4, 0, 0,  rioave , beiramar),\
	(2012, 28, 4, 0, 0,  guimaraes , pacos),\
	(2012, 28, 4, 0, 0,  maritimo , benfica),\
	(2012, 28, 4, 0, 0,  sporting , nacional),\
	(2012, 28, 4, 0, 0,  porto , setubal)\
	],\
	[ #28\
	(2012, 5, 5, 0, 0,  guimaraes , gilvicente),\
	(2012, 5, 5, 0, 0,  moreirense , braga),\
	(2012, 5, 5, 0, 0,  setubal , academica),\
	(2012, 5, 5, 0, 0,  nacional , porto),\
	(2012, 5, 5, 0, 0,  benfica , estoril),\
	(2012, 5, 5, 0, 0,  pacos , sporting),\
	(2012, 5, 5, 0, 0,  beiramar , maritimo),\
	(2012, 5, 5, 0, 0,  olhanense , rioave)\
	],\
	[ #29\
	(2012, 12, 5, 0, 0,  rioave , gilvicente),\
	(2012, 12, 5, 0, 0,  maritimo , guimaraes),\
	(2012, 12, 5, 0, 0,  sporting , olhanense),\
	(2012, 12, 5, 0, 0,  estoril , beiramar),\
	(2012, 12, 5, 0, 0,  academica , pacos),\
	(2012, 12, 5, 0, 0,  porto , benfica),\
	(2012, 12, 5, 0, 0,  braga , nacional),\
	(2012, 12, 5, 0, 0,  moreirense , setubal)\
	],\
	[ #30\
	(2012, 19, 5, 0, 0,  benfica , moreirense),\
	(2012, 19, 5, 0, 0,  setubal , braga),\
	(2012, 19, 5, 0, 0,  nacional , academica),\
	(2012, 19, 5, 0, 0,  pacos , porto),\
	(2012, 19, 5, 0, 0,  gilvicente , estoril),\
	(2012, 19, 5, 0, 0,  beiramar , sporting),\
	(2012, 19, 5, 0, 0,  olhanense , maritimo),\
	(2012, 19, 5, 0, 0,  guimaraes , rioave)\
	]\
]


for j in c.cmp_jornadas:
	num_jornada = j.jor_ordem
	for idx, val in enumerate(jogos[num_jornada]):
		jog = Jogo(\
			jog_numero_visitas = 0,\
			jog_ultima_alteracao = date,\
			jog_nome = "2012/2013:Liga:%s:%s:%s" % (str(num_jornada), val[5].clu_nome, val[6].clu_nome),\
			jog_epoca  = epoca,\
			jog_competicao = c,\
			jog_jornada  = j,\
			jog_data = datetime.datetime(val[0], val[2], val[1], val[3], val[4]),\
			jog_clube1 = val[5],\
			jog_clube2 = val[6]
		)
		jog.put()
