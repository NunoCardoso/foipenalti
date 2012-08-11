# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
epoca = Epoca.all().filter("epo_nome = ", "2012/2013").get()
date = datetime.datetime.now()

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

order = [porto, benfica, braga, sporting, maritimo, guimaraes, nacional, olhanense, gilvicente, pacos, setubal, beiramar, academica, rioave, estoril, moreirense]

cmp1 = Competicao.all().filter("cmp_nome = ","2011/2012:SuperTaca").get()
cjc1 = ClubeJogaCompeticao(cjc_clube=porto, cjc_competicao=cmp1 )
cjc1.put()
cjc2 = ClubeJogaCompeticao(cjc_clube=academica, cjc_competicao=cmp1 )
cjc2.put()

c1 = Competicao.all().filter("cmp_nome = ","2012/2013:Liga").get()
for idx, val in enumerate(order):
	cj = ClubeJogaCompeticao(cjc_clube=val, cjc_competicao=c1, cjc_classificacao_anterior= (idx+1) )
	cj.put()