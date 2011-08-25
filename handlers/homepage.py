# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 
import classes

from classes import *
from lib.mycachehandler import MyCacheHandler
from models import blog
from handlers.detalhe_jornada import DetalheJornada
from google.appengine.api import memcache
from lib import listas

class HomePage(MyCacheHandler):
		
	# memcache vars
	use_cache = True # use cache or not
	refreshen_cache = False # check if it needs to be refreshen
	cache_namespace = "homepage"
	cache_url = None

	#memcache values
	dados = None
	html = None
	
	epoca = None
	competicao = None
		
	def get(self):
		self.epoca = config.EPOCA_CORRENTE
		self.competicao = config.COMPETICAO_CORRENTE
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		
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
		post = blog.Post.all().order('-pub_date').get()
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
		
		posts = blog.Post.all().order('-pub_date').fetch(blogpost_limit)
		
		ultimo_jogo = listas.get_top_jogos_recentes()[0]
		ultimo_jogador = listas.get_top_jogadores_recentes()[0]
		ultimo_arbitro = listas.get_top_arbitros_recentes()[0]
		ultimo_jornada = listas.get_top_jornadas_recentes()[0]

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

		ultima_epoca_na_db = config.ULTIMA_EPOCA_NA_DB

		#logging.info("Rendering noticias")
		noticias_html = self.render_subdir('homepage','gera_mini_blog.html', {
			"posts": self.dados['posts']
		})		
			
		#logging.info("Rendering classificação real")
		classificacao_real_html = self.render_subdir('homepage','gera_classificacao_real.html', {
			"classificacao_real": self.dados['cl_real'],
			"competicao":self.competicao
		})		
			
		#logging.info("Rendering classificação virtual")
		classificacao_virtual_html = self.render_subdir('homepage','gera_classificacao_virtual.html', {
			"classificacao_virtual": self.dados['cl_virtual'],
			"competicao":self.competicao
		})
		
		#logging.info("Rendering jornada anterior")
		jornada_anterior_html = None
		if self.dados.has_key("jornada_anterior") and self.dados.has_key("jornada_anterior_dados") :
			jornada_anterior_html = self.render_subdir('homepage','gera_jornada.html', {
			"jornada": self.dados['jornada_anterior'],
			"jornada_dados": self.dados['jornada_anterior_dados']
			})
		
		#logging.info("Rendering jornada corrente")
		jornada_corrente_html = None
		if self.dados.has_key("jornada_corrente") and self.dados.has_key("jornada_corrente_dados") :
			jornada_corrente_html = self.render_subdir('homepage','gera_jornada.html', {
			"jornada": self.dados['jornada_corrente'],
			"jornada_dados": self.dados['jornada_corrente_dados']
		})
		
		#logging.info("Rendering jornada posterior")
		jornada_posterior_html = None
		if self.dados.has_key("jornada_posterior") and self.dados.has_key("jornada_posterior_dados") :
			jornada_posterior_html = self.render_subdir('homepage','gera_jornada.html', {
			"jornada": self.dados['jornada_posterior'],
			"jornada_dados": self.dados['jornada_posterior_dados']
		})

		#logging.info("Rendering homepage")
		html = self.render_subdir('homepage','homepage.html', {
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