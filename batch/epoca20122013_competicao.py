# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
epoca = Epoca.all().filter("epo_nome = ", "2012/2013").get()
date = datetime.datetime.now()

c1 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2012/2013:Liga",
	cmp_nome_completo = "Liga Zon Sagres", 
	cmp_tipo = "Liga",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=47487",
	cmp_link_foto = "img/competicao/20122013Liga.png",
	cmp_epoca = epoca,
	cmp_numero_jornadas = 30,
	cmp_lugares_liga_campeoes = [1L,2L],
	cmp_lugares_liga_europa = [4L,5L,6L],
	cmp_lugares_eliminatorias_liga_campeoes = [3L],
	cmp_lugares_descida = [15L,16L]
)
c1.put()

c2 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2012/2013:TacaPortugal",
	cmp_nome_completo = "Taca de Portugal", 
	cmp_tipo = "TacaPortugal",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=48227",
	cmp_link_foto = "img/competicao/20122013TacaPortugal.png",
	cmp_epoca = epoca,
	cmp_numero_jornadas = 6
)
c2.put()

c3 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2012/2013:TacaLiga",
	cmp_nome_completo = "Taca da Liga bwin Cup", 
	cmp_tipo = "TacaLiga",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=47493",
	cmp_link_foto = "img/competicao/20112012TacaLiga.png",
	cmp_epoca = epoca,
	cmp_numero_jornadas = 6
)
c3.put()

epo2 = Epoca.all().filter("epo_nome = ", "2011/2012").get()

c4 = Competicao(
	cmp_numero_visitas = 0,
	cmp_ultima_alteracao = date,
	cmp_nome = "2011/2012:SuperTaca",
	cmp_nome_completo = "Supertaca Candido de Oliveira", 
	cmp_tipo = "SuperTaca",
	cmp_link_zz = "http://www.zerozero.pt/edicao.php?id_edicao=47399",
	cmp_link_foto = "img/competicao/20112012SuperTaca.png",
	cmp_epoca = epo2,
	cmp_numero_jornadas = 1
)
c4.put()

