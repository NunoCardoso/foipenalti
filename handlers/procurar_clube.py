# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 

from classes import *
from lib import mymemcache
from externals.paging import *
from lib.myhandler import MyHandler
from lib import listas

class ProcurarClube(MyHandler):
	
	def get(self):

		jogos = None		
		num_resultados = self.request.get("nr")
		sid =self.get_sid_from_cookie()

		# critérios
		clube_id = self.request.get("clu")
		cache = self.request.get("cache")
		
		try:
			page_index = int(self.request.get("pg","1"))
		except ValueError:
			page_index = 1
			
		# values I want, either from memcache, or to generate now
		resultados = None
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
				for elem in ['clube']:
					cache = memcache.get(elem)
					if cache and cache['date'] > cacheresultados['date']:
						logging.info("Modelo '"+elem+"' tem elementos mais frescos ("+str(cache['date'])+") do que a cache desta procura ("+str(cacheresultados['date'])+")")
						cache_old = True
					
				if not cache_old:	
					logging.info ("Cache desta procura ("+str(cacheresultados['date'])+") ainda é fresca.")
				
			if not cacheresultados or cache_old:
			
				logging.info("Memcache para "+memcache_label+" é inexistente ou obsoleta. A gerar novos dados.")
				
				clubes = Clube.all()

				# primeiro nível: 1
				if clube_id:
					c = Clube.get_by_id(int(clube_id))
					if c:
						clubes.filter("__key__ = ", c.key())
		
# FIM DA FILTRAGEM
					
# INÍCIO DA PAGINAÇÃO
					
				# now, let's prepare the pages
		#		jogos.order("-jog_numero_visitas")
				myPagedQuery = PagedQuery(clubes, int(num_resultados))
				myPagedQuery.order("-clu_numero_visitas")
				results_page = myPagedQuery.fetch_page(page_index)
				
				myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
					url_root=re.sub("pg=\d+", "", self.request.url), page_field="pg")	
				results_page_links = myLinks.get_links()
				results_total = clubes.count()
				
				memcache_label = self.request.path+":"+self.request.query_string
				
#				logging.info("Setting new memcache data for "+memcache_label+" : "+str(results_page))
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
				"obj":"clube",
				"panel":"pesquisa",
				"total":results_total,
				"nr":num_resultados
			}, 
			"content":[]
			}

			if results_page:
			
				count = (page_index - 1)*int(num_resultados)
			
				for clube in results_page:
				
					count += 1
				
					resultados["content"].append({
					"nome":clube.clu_nome_curto,
					"foto":clube.clu_link_logo,
					"id":clube.key().id(),
					"click":count
					})

		flash_message = None
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(str(sid), namespace="flash")
			
		self.render_to_output('procurar_clube.html', {
			"clu_nome": clube_id,
			"num_resultados": num_resultados, 
			
			"flash":flash_message,
			
			# search results
			"results": resultados,
			"results_total": results_total,
			"results_page_links":results_page_links,

			# memcache stuff
			"clubes": listas.get_lista_clubes(), 
			"resultados": [15, 30, 40]
		})
		
