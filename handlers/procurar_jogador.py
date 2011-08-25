# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler
from lib import listas

class ProcurarJogador(MyHandler):
	
	def get(self):
		
		jogadores = None
		
		num_resultados = self.request.get("nr")
		jgd_nome = self.request.get("jgd")
		jgd_clube = self.request.get("clu")
		jgd_epoca = self.request.get("epo")
		jgd_numero = self.request.get("num")
		cache = self.request.get("cache")
		
		try:
			page_index = int(self.request.get("pg","1"))
		except ValueError:
			page_index = 1
			
		# values I want, either from memcache, or to generate now
		resultados = None
		ctjogadores = None 
		results_page = None
		results_total = None
		results_page_links = None
		
		# ok, if we have num_resultados, we have a search
		if num_resultados: 
			
			# let's take off the page. THe cache stores the full results, not the page view
			memcache_label = self.request.path+":"+self.request.query_string
			
			logging.info("A procurar memcache por "+memcache_label)
			# if this search is in memcache, let's use it
			cacheresultados = memcache.get(memcache_label)
			
			# IF NOT or if it's obsolete, LET'S REBUILD IT
			cache_old = None
			if cacheresultados and cache != "false": 
				# let's check if there are new stuff from: jogador, clube_tem_jogador
				
				cache_old = False
				for elem in ['jogador','clube_tem_jogador']:
					cache = memcache.get(elem)
					if cache and cache['date'] > cacheresultados['date']:
						logging.info("Modelo '"+elem+"' tem elementos mais frescos ("+str(cache['date'])+") do que a cache desta procura ("+str(cacheresultados['date'])+")")
						cache_old = True
					
				if not cache_old:	
					logging.info ("Cache desta procura ("+str(cacheresultados['date'])+") ainda é fresca.")
				
			if not cacheresultados or cache_old:
			
				logging.info("Memcache para "+memcache_label+" é inexistente ou obsoleta. A gerar novos dados.")
				
				ctjogadores = ClubeTemJogador.all()
			
				# if jog_epoca (id)
				if jgd_epoca:
					epoca = Epoca.get_by_id(int(jgd_epoca))
					ctjogadores.filter("ctj_epocas =", epoca.key())
					
				if jgd_numero:
					ctjogadores.filter("ctj_numero = ", int(jgd_numero))
					logging.info("Fitro:jgd_numero "+ jgd_numero)
				
				# if jog_clube (id)
				if jgd_clube:
					clube = Clube.get_by_id(int(jgd_clube))
					ctjogadores.filter("ctj_clube = ", clube)
					logging.info("Fitro:clube "+ clube.__str__())

				# if jog_nome
				if jgd_nome:
					jogadores = Jogador.all().filter("jgd_nome = ",jgd_nome).order("jgd_nome")
					logging.info("filtro: jgd_nome")
					ctjogadores.filter("ctj_jogador in ", jogadores.fetch(1000))
								
				#data = ctjogadores.fetch(int(num_resultados))
				
				logging.info("Got new ctjogadores, count = "+str(ctjogadores.count())+" (num_resultados = "+str(num_resultados)+")")
				
				# now, let's prepare the pages
				myPagedQuery = PagedQuery(ctjogadores, int(num_resultados))
				# não há ordem, são ctj
				#myPagedQuery.order("jgd_numero_visitas")
				results_page = myPagedQuery.fetch_page(page_index)
				myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
					url_root=re.sub("&?pg=\d+", "", self.request.url), page_field="pg")	
				results_page_links = myLinks.get_links()
				results_total = ctjogadores.count()
				
				memcache_label = self.request.path+":"+self.request.query_string
				
				# let's put search results on cache
				memcache.set(memcache_label, 
				{"date":datetime.datetime.today() , "results_page":results_page, 
					"results_total":results_total, "page":page_index, 
					"results_page_links":results_page_links},time=86400)
				
			else:
				logging.info("Memcache existe para "+memcache_label+", a obter dados da memcache")
				results_page = cacheresultados['results_page']
				results_total = cacheresultados['results_total']
				results_page_links = cacheresultados['results_page_links']

			resultados = {
			"header":{
				"obj":"jogador",
				"panel":"pesquisa",
				"total":results_total,
				"nr":num_resultados
				}, 
			"content":[]
			}

			if results_page:
			
				count = (page_index - 1)*int(num_resultados)
			
				for ctj in results_page:
				
					count += 1
				
					resultados["content"].append({
					"nome":ctj.ctj_jogador.jgd_nome,
					"foto":ctj.ctj_jogador.jgd_link_foto,
					"numero":ctj.ctj_jogador.jgd_numero,
					"clube":ctj.ctj_jogador.jgd_clube_actual.clu_nome_curto,
					"clube_id":ctj.ctj_jogador.jgd_clube_actual.key().id(),
					"id":ctj.ctj_jogador.key().id(),
					"click":count
					})

		flash_message = memcache.get("flash")
		if flash_message:
			memcache.delete("flash")

		self.render_to_output('procurar_jogador.html', {
			## feedback of get variables
			"jgd_nome": jgd_nome,
			"jgd_clube": jgd_clube,
			"jgd_epoca": jgd_epoca,
			"jgd_numero": jgd_numero,
			"num_resultados": num_resultados, 
			
			# search results
			"results": resultados,
			"results_total": results_total,
			"results_page_links":results_page_links,

			"flash":flash_message,

			# memcache stuff
			"clubes": listas.get_lista_clubes(),
			"epocas": listas.get_lista_epocas(),
			"resultados": [15, 30, 40]
		})
