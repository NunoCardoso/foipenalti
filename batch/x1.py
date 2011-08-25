# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
epoca = Epoca.all().filter("epo_nome = ", "2011/2012").get()
date = datetime.datetime.now()

c1 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2011/2012:Liga",
	cmp_nome_completo = "Liga Zon Sagres", 
	cmp_tipo = "Liga",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=22951",
	cmp_link_foto = "img/competicao/20102011Liga.png",
	cmp_epoca = epoca,
	cmp_numero_jornadas = 30,
	cmp_lugares_liga_campeoes = [1L],
	cmp_lugares_liga_europa = [3L,4L,5L,6L],
	cmp_lugares_eliminatorias_liga_campeoes = [2L],
	cmp_lugares_descida = [15L,16L]
)
c1.put()

c2 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2011/2012:TacaPortugal",
	cmp_nome_completo = "Taca de Portugal", 
	cmp_tipo = "TacaPortugal",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=24179",
	cmp_link_foto = "img/competicao/20112012TacaPortugal.png",
	cmp_epoca = epoca,
	cmp_numero_jornadas = 6
)
c2.put()

epo2011 = Epoca.all().filter("epo_nome = ", "2010/2011").get()

c3 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2010/2011:SuperTaca",
	cmp_nome_completo = "Supertaca Candido de Oliveira", 
	cmp_tipo = "SuperTaca",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=22309",
	cmp_link_foto = "img/competicao/20102011SuperTaca.png",
	cmp_epoca = epo2011,
	cmp_numero_jornadas = 1
)
c3.put()

c4 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2011/2012:TacaLiga",
	cmp_nome_completo = "Taca da Liga bwin Cup", 
	cmp_tipo = "TacaLiga",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=22949",
	cmp_link_foto = "img/competicao/20112012TacaLiga.png",
	cmp_epoca = epoca,
	cmp_numero_jornadas = 6
)
c4.put()


cl1 = Clube.all().filter("clu_nome = ", "Porto").get()
cl2 = Clube.all().filter("clu_nome = ", "Guimaraes").get()
cmp1 = Competicao.all().filter("cmp_nome = ","2010/2011:SuperTaca").get()
cjc1 = ClubeJogaCompeticao(
 cjc_clube=cl1,
 cjc_competicao=cmp1 )
cjc1.put()
cjc2 = ClubeJogaCompeticao(
 cjc_clube=cl2,
 cjc_competicao=cmp1 )
cjc2.put()