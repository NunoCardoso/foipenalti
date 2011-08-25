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

class ProcurarArbitro(MyHandler):
	
	def get(self):
		
		jogadores = None
		
		num_resultados = self.request.get("nr")
		
		# variáveis get que correspondem aos valores do form
		arb_nome = self.request.get("arb") #ID
		arb_clube1 = self.request.get("clu1") #ID
		arb_clube2 = self.request.get("clu2") #ID
		cache = self.request.get("cache") #ID
		
		try:
			page_index = int(self.request.get("pg","1"))
		except ValueError:
			page_index = 1
			
		# values I want, either from memcache, or to generate now
		arbitros = None 
		resultados = None
		results_page = None
		results_total = None
		results_page_links = None
		
		# ok, if we have num_resultados, we have a search
		if num_resultados: 
			
			# let's take off the page. THe cache stores the full results, not the page view
			memcache_label = self.request.path+":"+self.request.query_string
			
			# if this search is in memcache, let's use it
			cacheresultados = memcache.get(memcache_label)
			
			# IF NOT or if it's obsolete, LET'S REBUILD IT
			cache_old = None
			if cacheresultados and cache != "false": 
				# let's check if there are new stuff from: arbitro, jogo
				
				cache_old = False
				
				for elem in ['arbitro','jogo']:
					cache = memcache.get(elem)
					if cache and cache['date'] > cacheresultados['date']:
						logging.info("Modelo '"+elem+"' tem elementos mais frescos ("+str(cache['date'])+") do que a cache desta procura ("+str(cacheresultados['date'])+")")
						cache_old = True
					
				if not cache_old:	
					logging.info ("Cache desta procura ("+str(cacheresultados['date'])+") ainda é fresca.")
				
			if not cacheresultados or cache_old:
			
				logging.info("Memcache para "+memcache_label+" é inexistente ou obsoleta. A gerar novos dados.")
				
				arbitros = Arbitro.all()
				
				if arb_clube1:
					clube1 = Clube.get_by_id(int(arb_clube1))
					jogos = None
					jogos2 = None
					if arb_clube2:
						clube2 = Clube.get_by_id(int(arb_clube2))
						jogos = Jogo.gql("WHERE jog_clube1 = :1 AND jog_clube2 = :2",  clube1, clube2)
						#logging.info("Fitro: jog_clube1 "+ str(clube1)+" AND jog_clube2 = "+ str(clube2))
					else: 
						jogos = Jogo.gql("WHERE jog_clube1 = :1",  clube1)
						jogos2 = Jogo.gql("WHERE jog_clube2 = :1",  clube1)
						#logging.info("Fitro: jog_clube1 "+ str(clube1)+" OR jog_clube2 = "+ str(clube1))
					
					arbs = []	
					if jogos: 
						for jogo in jogos:
							if jogo.jog_arbitro:
								if not jogo.jog_arbitro.key().id() in arbs: 
									arbs.append(jogo.jog_arbitro.key())
					if jogos2: 
						for jogo in jogos2:
							if jogo.jog_arbitro:
								if not jogo.jog_arbitro.key().id() in arbs: 
									arbs.append(jogo.jog_arbitro.key())
					arbitros.filter("__key__ in",arbs)
					
				# arb_nome is an ID, really...
				if arb_nome:
					arbitro_key = Arbitro.get_by_id(int(arb_nome))
					arbitros.filter("__key__ IN",[arbitro_key.key()]) 
					
					#logging.info("filtro: arb_nome "+arb_nome)
												
				#logging.info("Got new arbitros, count = "+str(arbitros.count())+" (num_resultados = "+str(num_resultados)+")")
				
				# now, let's prepare the pages
				myPagedQuery = PagedQuery(arbitros, int(num_resultados))
				myPagedQuery.order("-arb_numero_visitas")
				results_page = myPagedQuery.fetch_page(page_index)
				myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
					url_root=re.sub("&?pg=\d+", "", self.request.url), page_field="pg")	
				results_page_links = myLinks.get_links()
				results_total = arbitros.count()
				
				memcache_label = self.request.path+":"+self.request.query_string
				
				# let's put search results on cache
				memcache.set(memcache_label, 
				{"date":datetime.datetime.today() , "results_page":results_page, 
					"results_total":arbitros.count(), "page":page_index, 
					"results_page_links":results_page_links},time=86400)
				
			else:
				logging.info("Memcache existe para "+memcache_label+", a obter dados da memcache")
				results_page = cacheresultados['results_page']
				results_total = cacheresultados['results_total']
				results_page_links = cacheresultados['results_page_links']
		
			resultados = {
			"header":{
				"obj":"arbitro",
				"panel":"pesquisa",
				"total":results_total,
				"nr":num_resultados
			}, 
			"content":[]
			}

			if results_page:
			
				count = (page_index - 1)*int(num_resultados)
			
				for arbitro in results_page:
				
					count += 1
				
					resultados["content"].append({
					"nome":arbitro.arb_nome,
					"foto":arbitro.arb_link_foto,
					"id":arbitro.key().id(),
					"click":count
					})

		flash_message = memcache.get("flash")
		if flash_message:
			memcache.delete("flash")

		self.render_to_output('procurar_arbitro.html', {
			"arb_nome": arb_nome,
			"arb_clube1": arb_clube1,
			"arb_clube2": arb_clube2,
			"num_resultados": num_resultados, 
			
			# search results
			"results": resultados,
			"results_total": results_total,
			"results_page_links":results_page_links,

			"flash":flash_message,

			# memcache stuff
			"clubes": listas.get_lista_clubes(),
			"arbitros": listas.get_lista_arbitros(),
			"resultados": [15, 30, 40]
		})
