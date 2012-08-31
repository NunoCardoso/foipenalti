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

class ProcurarEpoca(MyHandler):
	
	def get(self):

		jogos = None		
		num_resultados = self.request.get("nr")
		sid =self.get_sid_from_cookie()

		# critérios
		epoca_id = self.request.get("epo")
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
			
			# if this search is in memcache, let's use it
			cacheresultados = memcache.get(memcache_label)
			
			# IF NOT or if it's obsolete, LET'S REBUILD IT
			cache_old = None
			if cacheresultados and cache != "false": 
				# let's check if there are new stuff from: jogador, clube_tem_jogador
				
				cache_old = False
				for elem in ['epoca']:
					cache = memcache.get(elem)
					if cache and cache['date'] > cacheresultados['date']:
						cache_old = True
					
			if not cacheresultados or cache_old:
			
				epocas = Epoca.all()

				# primeiro nível: 1
				if epoca_id:
					e = Epoca.get_by_id(int(epoca_id))
					if e:
						epocas.filter("__key__ = ", e.key())
		
# FIM DA FILTRAGEM
					
# INÍCIO DA PAGINAÇÃO
					
				# now, let's prepare the pages
		#		jogos.order("-jog_numero_visitas")
				myPagedQuery = PagedQuery(epocas, int(num_resultados))
				myPagedQuery.order("-epo_numero_visitas")
				results_page = myPagedQuery.fetch_page(page_index)
				
				myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
					url_root=re.sub("pg=\d+", "", self.request.url), page_field="pg")	
				results_page_links = myLinks.get_links()
				results_total = epocas.count()
				
				memcache_label = self.request.path+":"+self.request.query_string
				
				# let's put search results on cache
				memcache.set(memcache_label, 
				{"date":datetime.datetime.today() , "results_page":results_page, 
					"results_total":results_total, "page":page_index, 
					"results_page_links":results_page_links},time=86400)
				
			else:
				results_page = cacheresultados['results_page']
				results_total = cacheresultados['results_total']
				results_page_links = cacheresultados['results_page_links']
		
			resultados = {
			"header":{
				"obj":"epoca",
				"panel":"pesquisa",
				"total":results_total,
				"nr":num_resultados
			}, 
			"content":[]
			}

			if results_page:
			
				count = (page_index - 1)*int(num_resultados)
			
				for epoca in results_page:
				
					count += 1
				
					resultados["content"].append({
					"nome":epoca.epo_nome,
					"id":epoca.key().id(),
					"click":count
					})
		
		flash_message = None
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(str(sid), namespace="flash")
						
		self.render_to_output('procurar_epoca.html', {
			"epo_nome": epoca_id,
			"num_resultados": num_resultados, 
			
			"flash":flash_message,
			
			# search results
			"results": resultados,
			"results_total": results_total,
			"results_page_links":results_page_links,

			# memcache stuff
			"epocas": listas.get_lista_epocas(), 
			"resultados": [15, 30, 40]
		})
		
