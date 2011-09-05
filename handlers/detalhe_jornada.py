# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from lib import mymemcache
from google.appengine.api import memcache
from lib.mycachehandler import MyCacheHandler

class DetalheJornada(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_jornada"
	cache_url = None

	#memcache values
	dados = None
	html = None
	sid = None

	# get vars
	jornada = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.jornada:
			error = u"Erro: Essa jornada ainda não está disponível."
			logging.error(error)
			new_sid = mymemcache.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.redirect(mymemcache.add_sid_to_url(self.referer, new_sid))
			return

		self.checkCacheFreshen()
		self.requestHandler()
		self.jornada.jor_numero_visitas += 1
		self.jornada.put() 
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
		
		if data_cache and self.jornada.jor_ultima_alteracao > data_cache:
			self.refreshen_cache = True

	def renderDados(self):
		jornada_dados = {
			"datas":{} # no início, é uma hash com key:data e value:list com 
		 # entradas {jogo, jogador_clube1, jogador_clube2}, 
		}
		for jogo in self.jornada.jor_jogos.order("jog_data"):
		
			date = jogo.jog_data.date()
			if not jornada_dados["datas"].has_key(date):
				jornada_dados["datas"][date] = []
			
			elem = {"jogo":jogo, "jogadores_clube1":[], "jogadores_clube2":[]}

			for jjj in jogo.jog_jogadores:
				if len(jjj.jjj_golos_minutos) > 0:
					if jjj.jjj_jogador.jgd_clube_actual.key() == jogo.jog_clube1.key():
						elem["jogadores_clube1"].append({
						"jogador":jjj.jjj_jogador,
						"golos":jjj.jjj_golos_minutos,
						"tipos_golos":jjj.jjj_golos_tipos
					})
					else:
						elem["jogadores_clube2"].append({
						"jogador":jjj.jjj_jogador,
						"golos":jjj.jjj_golos_minutos,
						"tipos_golos":jjj.jjj_golos_tipos
					})
			
			jornada_dados["datas"][date].append(elem)		

		lista_datas = []
		for key in sorted(jornada_dados["datas"].iterkeys()):
			lista_datas.append({"data":key, "jogos":jornada_dados["datas"][key]})
	
		jornada_dados["datas"] = lista_datas
	# {"jornada":{
	#      "datas":[
	#              {"data":"2010-09-18",
	#					 "jogos":[<jogo:jogo1, jogadores_clube1, jogadores_clube2>,
	#					 			[<jogo:jogo2, jogadores_clube1, jogadores_clube2>]
	#					},
	#					{"data":"2010-09-19",
	#					 "jogos":[<jogo:jogo3, jogadores_clube1, jogadores_clube2>,
	#					 			[<jogo:jogo4, jogadores_clube1, jogadores_clube2>]
	#					}
	#				]
	#      }
	# }

		return {"jornada":jornada_dados}
		
	def renderHTML(self):
		flash_message = None
		if self.sid:
			flash_message = memcache.get(str(self.sid), namespace="flash")
			if flash_message:
				memcache.delete(str(self.sid), namespace="flash")
				
		html = self.render('detalhe_jornada.html', {
			## feedback of get variables
			"jornada":self.jornada,
			"jornada_dados": self.dados["jornada"],
			"flash":flash_message
		})
		
		return html
		
	def decontaminate_vars(self):
		
		jor_id = None
		jornada = None

		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/detalhe_competicao"
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		self.sid = self.request.get("sid")
		
		if self.request.get("id"):
			try:
				jornada = Jornada.get_by_id(int(self.request.get("id")))
			except:
				pass
		
		if not jornada:
			if self.request.get("jornada"):
				
				try:
					jornada = Jornada.all().filter("jor_nome =",self.request.get("jornada")).get()
				except:
					pass

		if not jornada:
			logging.info(self.request.get("competicao")+":"+self.request.get("jornada"))
			if self.request.get("competicao"):
				try:
					jornada = Jornada.all().filter("jor_nome =", self.request.get("competicao")+":"+self.request.get("jornada")).get()
				except:
					pass
				
		if jornada:

			self.jornada = jornada
		
			self.cache_url = self.request.path+"?id="+str(jornada.key().id())
