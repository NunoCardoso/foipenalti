# -*- coding: utf-8 -*-

import os
import datetime
import re
import config 
import classes
import errors

from classes import *

from lib.mycachehandler import MyCacheHandler
from handlers.detalhe_jornada import DetalheJornada
from google.appengine.api import memcache
from lib import listas
from lib.tabela_icc import TabelaICC
from lib.grafico_icc import GraficoICC
from lib.grafico_ica import GraficoICA

class HomePage(MyCacheHandler):
		
	# memcache vars
	use_cache = True # use cache or not
	refreshen_cache = False # check if it needs to be refreshen
	cache_namespace = "homepage"
	cache_url = None
	render_this_page_without_main = False

	#memcache values
	dados = None
	html = None
	title = None

	epoca = None
	competicao = None

	homepage_info = [	
	{"image":u"img/homepage/20130519_porto.jpg",
	"title":u"Porto Porto Porto! Tricampeão nacional!",
	"source_url":u"http://desporto.sapo.pt",
	"source_title":u"SAPO Desporto",
	"description":u"No campeonato mais emocionante dos últimos anos, FC Porto ganha ao foto-finish. "+
        "Veja a <a href='http://www.foipenalti.com/detalhe_jogo?jogo=2012/2013:Liga:30:PacosFerreira:Porto'>"+
	u"ficha do jogo Paços de Ferreira 0-2 FC Porto</A>."}
	]	
	
	def get(self):
		try:
			self.epoca = self.getConstants().getEpocaCorrente()
			self.competicao = self.getConstants().getCompeticaoCorrente()
			self.decontaminate_vars()
			self.checkCacheFreshen()
			self.requestHandler()
		except:
			return errors.overquota(self)
		return 
		
	def checkCacheFreshen(self):
		data_cache = None # data do HRML gerado em cache
		
		self.softcache_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_html:
			data_cache = self.softcache_html['date']
		else:
			self.hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if self.hardcache_html:
				data_cache = self.hardcache_html.cch_date
		
		
		# onde é que estou dependente? de: blog e de competição, basicamente
		post = Post.all().order('-pub_date').get()
		jornada = Jornada.all().order('-jor_ultima_alteracao').get()
		
		if data_cache and post.pub_date and jornada:
			if post.pub_date > data_cache or jornada.jor_ultima_alteracao > data_cache:
				self.refreshen_cache = True

	def renderDados(self):
		
		blogpost_limit = 4

# CRIAR CARROSSEL JORNADAS
		now = datetime.datetime.now()
	#	now_plus_one_day = now + datetime.timedelta(days=1)
		jornadas_passadas = Jornada.all().filter("jor_competicao = ", self.competicao ).filter("jor_data <= ",now).order("-jor_data")
		jornadas_futuras = Jornada.all().filter("jor_competicao = ", self.competicao ).filter("jor_data > ",now).order("jor_data")
		
		jornadas_anteriores = [] 
		for j in jornadas_passadas.fetch(2):
			jornadas_anteriores.append(j)
		jornadas_posteriores = []
		for j in jornadas_futuras.fetch(2):
			jornadas_posteriores.append(j)
			
		jornada_corrente = None
		jornada_posterior = None
		jornada_anterior = None
		
# qual é a jornada corrente? Se a jornada futura já tem jogos de hoje...
		corrente = False
		if len(jornadas_posteriores) > 0:
			for jogo in jornadas_posteriores[0].jor_jogos:
				if jogo.jog_data < now:
					corrente = True
		
		if corrente:
			if len(jornadas_posteriores) > 0:
				jornada_corrente = jornadas_posteriores[0]
			if len(jornadas_posteriores) > 1:
				jornada_posterior = jornadas_posteriores[1]
			if len(jornadas_anteriores) > 0:
				jornada_anterior = jornadas_anteriores[0]
		else:
			if len(jornadas_anteriores) > 0:
				jornada_corrente = jornadas_anteriores[0]
			if len(jornadas_posteriores) > 0:
				jornada_posterior = jornadas_posteriores[0]
			if len(jornadas_anteriores) > 1:
				jornada_anterior = jornadas_anteriores[1]

		jor = DetalheJornada()
		jor_posterior_dados = None
		jor_corrente_dados = None
		jor_anterior_dados = None
		
		if jornada_anterior != None:
			jor.jornada=jornada_anterior
			jor_anterior_dados = jor.renderDados()
		if jornada_corrente != None:
			jor.jornada=jornada_corrente
			jor_corrente_dados = jor.renderDados()
		if jornada_posterior != None:
			jor.jornada=jornada_posterior
			jor_posterior_dados = jor.renderDados()

# CRIAR CARROSSEL CALENDÁRIO
		jogos_calendario, last_month, last_year, today_month, today_year, \
			next_month, next_year = self.gera_carrossel_calendario()
		
# CRIAR CARROSSEL CLASSIFICAÇÃO
		acu_class_real = classes.getAcumuladorCompeticao(self.competicao, config.VERSAO_ACUMULADOR,"classificacao_real")
		cl_real = None
		cl_virtual = None
		
		if acu_class_real:
			cl_real = acu_class_real.acuc_content["classificacao_real"]
		
		acu_class_virtual = classes.getAcumuladorCompeticao(self.competicao, config.VERSAO_ACUMULADOR,"classificacao_virtual")
		if acu_class_virtual:
			cl_virtual = acu_class_virtual.acuc_content["classificacao_virtual"]
			
		lista_clubes = listas.get_lista_clubes()
		clus = {}
		for clube in lista_clubes: 
			clus[clube.key().id()] = clube
	
		if cl_real:
			for idx, item in enumerate(cl_real["total"]):
				cl_real["total"][idx]["clube"] = clus[cl_real["total"][idx]["clu"]]
		if cl_virtual:
			for idx, item in enumerate(cl_virtual["total"]):
				cl_virtual["total"][idx]["clube"] = clus[cl_virtual["total"][idx]["clu"]]

# CRIAR BLOG POSTS		
		posts = Post.all().order('-pub_date').fetch(blogpost_limit)

# CRIAR TOPS CLUBES ICC
		grafico = GraficoICC()
		grafico.load_grafico_icc_for_epoca(self.epoca)

		top_clubes_beneficiados_icc = grafico.get_top_beneficiados(3)
		top_clubes_prejudicados_icc =  grafico.get_top_prejudicados(3)
		
		for idx, val in enumerate(top_clubes_beneficiados_icc):
			top_clubes_beneficiados_icc[idx]["clube"] = Clube.get_by_id(top_clubes_beneficiados_icc[idx]["clu"])
		for idx, val in enumerate(top_clubes_prejudicados_icc):
			top_clubes_prejudicados_icc[idx]["clube"] = Clube.get_by_id(top_clubes_prejudicados_icc[idx]["clu"])	

# CRIAR TOPS ARBITROS ICA
		grafico_ica = GraficoICA()
		grafico_ica.load_grafico_ica_for_epoca(self.epoca)

		top_arbitros_bons_ica = grafico_ica.get_top_bons(3)
		top_arbitros_maus_ica = grafico_ica.get_top_maus(3)

		for idx, val in enumerate(top_arbitros_bons_ica):
			top_arbitros_bons_ica[idx]["arbitro"] = Arbitro.get_by_id(top_arbitros_bons_ica[idx]["arb"])
		for idx, val in enumerate(top_arbitros_maus_ica):
			top_arbitros_maus_ica[idx]["arbitro"] = Arbitro.get_by_id(top_arbitros_maus_ica[idx]["arb"])	

# CRIAR TOPS 3 GRANDES/ÁRBITROS (TABELA ICC)	
		tabela_icc = TabelaICC()
		tabela_icc.load_tabela_icc_for_epoca(self.epoca)
		top_tabela_icc_3_grandes = tabela_icc.get_top_arbitros_para_3_grandes()

		dados = {
			"cl_real":cl_real["total"],
			"cl_virtual":cl_virtual["total"],
			
			"jogos_calendario":jogos_calendario,
			
			"last_month":last_month, 
			"last_year":last_year, 
			"today_month":today_month,
			"today_year":today_year, 
			"next_month":next_month, 
			"next_year":next_year,
			
			"posts":posts,
			
			"top_clubes_beneficiados_icc":top_clubes_beneficiados_icc,
			"top_clubes_prejudicados_icc":top_clubes_prejudicados_icc,
			
			"top_tabela_icc_3_grandes":top_tabela_icc_3_grandes,
			
			"top_arbitros_bons_ica":top_arbitros_bons_ica,
			"top_arbitros_maus_ica":top_arbitros_maus_ica,
			
			"jogadores_populares":listas.get_top_jogadores_populares(),
			"clubes_populares":listas.get_top_clubes_populares(),
			"jogos_populares":listas.get_top_jogos_populares(),
			"lances_populares":listas.get_top_lances_populares(),
			"arbitros_populares":listas.get_top_arbitros_populares(),

			"jogadores_recentes":listas.get_top_jogadores_recentes(),
			"jogos_recentes":listas.get_top_jogos_recentes(),
			"lances_recentes":listas.get_top_lances_recentes(),
			"arbitros_recentes":listas.get_top_arbitros_recentes(),
		}
		
		if jornada_anterior != None:
			dados["jornada_anterior"] = jornada_anterior
		dados["jornada_corrente"]=jornada_corrente
		if jornada_posterior != None:
			dados["jornada_posterior"]=jornada_posterior
			
		if jor_anterior_dados != None:
			dados["jornada_anterior_dados"]=jor_anterior_dados["jornada"]
		if jor_corrente_dados != None:
			dados["jornada_corrente_dados"]=jor_corrente_dados["jornada"]
		if jor_posterior_dados != None:
			dados["jornada_posterior_dados"]=jor_posterior_dados["jornada"]

		return dados

	def renderHTML(self):

		ultima_epoca_na_db = self.getConstants().getUltimaEpocaNaDB()

		noticias_html = self.render_subdir('homepage','gera_mini_blog.html', {
			"posts": self.dados['posts']
		})		
			
		classificacao_real_html = self.render_subdir('homepage','gera_classificacao_real.html', {
			"classificacao_real": self.dados['cl_real'],
			"competicao":self.competicao
		})		
			
		classificacao_virtual_html = self.render_subdir('homepage','gera_classificacao_virtual.html', {
			"classificacao_virtual": self.dados['cl_virtual'],
			"competicao":self.competicao
		})
		
		jornada_anterior_html = None
		if self.dados.has_key("jornada_anterior") and self.dados.has_key("jornada_anterior_dados") :
			jornada_anterior_html = self.render_subdir('homepage','gera_jornada.html', {
			"jornada": self.dados['jornada_anterior'],
			"jornada_dados": self.dados['jornada_anterior_dados']
			})
		
		jornada_corrente_html = None
		if self.dados.has_key("jornada_corrente") and self.dados.has_key("jornada_corrente_dados") :
			jornada_corrente_html = self.render_subdir('homepage','gera_jornada.html', {
			"jornada": self.dados['jornada_corrente'],
			"jornada_dados": self.dados['jornada_corrente_dados']
		})
		
		jornada_posterior_html = None
		if self.dados.has_key("jornada_posterior") and self.dados.has_key("jornada_posterior_dados") :
			jornada_posterior_html = self.render_subdir('homepage','gera_jornada.html', {
			"jornada": self.dados['jornada_posterior'],
			"jornada_dados": self.dados['jornada_posterior_dados']
		})

		top_arbitros_ica_html = self.render_subdir('homepage','gera_tops_arbitros_ica.html', {
			"top_arbitros_bons_ica": self.dados['top_arbitros_bons_ica'],
			"top_arbitros_maus_ica": self.dados['top_arbitros_maus_ica']
		})
		
		top_clubes_icc_html = self.render_subdir('homepage','gera_tops_clubes_icc.html', {
			"top_clubes_beneficiados_icc": self.dados['top_clubes_beneficiados_icc'],
			"top_clubes_prejudicados_icc": self.dados['top_clubes_prejudicados_icc']
		})
		
		top_3_grandes_arbitros_html = self.render_subdir('homepage','gera_3_grandes_arbitros.html', {
			"top_tabela_icc_3_grandes": self.dados['top_tabela_icc_3_grandes']
		})
		
		html = self.render_subdir('homepage','homepage.html', {
		
			"homepage_info":self.homepage_info,
			
			"classificacao_real_html":classificacao_real_html,
			"classificacao_virtual_html":classificacao_virtual_html,
			
			"jornada_anterior_html":jornada_anterior_html,
			"jornada_corrente_html":jornada_corrente_html,
			"jornada_posterior_html":jornada_posterior_html,
			
			"noticias_html": noticias_html,
						
			"jogos_calendario": self.dados['jogos_calendario'],
			
			"last_month":self.dados['last_month'],
			"last_year":self.dados['last_year'],
			"today_month":self.dados['today_month'],
			"today_year":self.dados['today_year'],
			"next_month":self.dados['next_month'],
			"next_year":self.dados['next_year'],
			
			"top_arbitros_ica_html":top_arbitros_ica_html,
			"top_clubes_icc_html":top_clubes_icc_html,
			"top_3_grandes_arbitros_html":top_3_grandes_arbitros_html,
				
			"jogadores_populares":self.dados['jogadores_populares'],
			"clubes_populares":self.dados['clubes_populares'],
			"jogos_populares":self.dados['jogos_populares'],
			"lances_populares":self.dados['lances_populares'],
			"arbitros_populares":self.dados['arbitros_populares'],
			
			"jogadores_recentes":self.dados['jogadores_recentes'],
			"jogos_recentes":self.dados['jogos_recentes'],
			"lances_recentes":self.dados['lances_recentes'],
			"arbitros_recentes":self.dados['arbitros_recentes'],

			"competicoes":listas.get_lista_competicoes_por_visitas(),
			"epocas":listas.get_lista_epocas(),
			"epoca":self.epoca, 
			"competicao":self.competicao,
			"data":datetime.datetime.now()
		})
	
		return html

	def renderTitle(self):
		return u"Página Principal"
		
	def decontaminate_vars(self):
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False
	
		self.cache_url = "/"
	
	def url_jornada(self, jornada):
		return u"<A HREF='/detalhe_jornada?id=%s'>%s %s</A>" % (str(jornada.key().id()), jornada.jor_competicao.cmp_nome_completo, jornada.jor_nome_completo)

	def url_jogo(self, jogo):
		return "<A HREF='/detalhe_jogo?id=%s'>%s</A>" % (str(jogo.key().id()), jogo.printjogo())
		
	def gera_carrossel_calendario(self):	

		# como isto é para Javascript, de notar que os meses começam em 0 e acabam em 11!
		today = datetime.date.today()
		today_month = today.month - 1
		today_year = today.year
		last_month = today_month
		last_year = today.year
		next_month = today_month
		next_year = today.year
		nnext_month = today_month
		nnext_year = today.year
		
		if today_month == 0:
			last_month = 11
			last_year = today_year - 1
		elif today_month == 11:
			next_month = 0
			next_year = today_year + 1
			nnext_month = 1
			nnext_year = today_year + 1
		elif today_month == 10:
			next_month = 11
			nnext_month = 0
			nnext_year = today_year + 1
		else:
			last_month = today_month - 1
			next_month = today_month + 1
			nnext_month = today_month + 2

		lower_date = datetime.date(last_year, last_month + 1, 1)
		upper_date = datetime.date(nnext_year, nnext_month + 1, 1)
		
		jogos = Jogo.all().filter("jog_data >= ", lower_date).filter("jog_data < ",upper_date).order("jog_data")
		
		# vamos organizar por meses
		jogos_calendario = {}
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
			if not self.url_jornada(j.jog_jornada) in jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jornadas"]:
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jornadas"].append(self.url_jornada(j.jog_jornada))
				
			# labels de jogos 
			if not jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day].has_key("jogos"):
				jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jogos"] = []
			jogos_calendario[j.jog_data.year][j.jog_data.month - 1][j.jog_data.day]["jogos"].append(self.url_jogo(j))
		
		return jogos_calendario, last_month, last_year, today_month, today_year, next_month, next_year 
