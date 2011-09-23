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

class ProcurarJogo(MyHandler):
	
	def get(self):

		jogos = None		
		num_resultados = self.request.get("nr")
		# critérios
		jog_realizados = self.request.get("jr")
#		jog_epoca = self.request.get("ep")
		jog_competicao = self.request.get("cmp")
#		jog_jornada_numero = self.request.get("jr")
		jog_clube1 = self.request.get("clu1")
		jog_clube2 = self.request.get("clu2")
		jog_arbitro = self.request.get("arb")
		jog_golos_clube1 = self.request.get("gol1")
		jog_golos_clube2 = self.request.get("gol2")
		jog_jogador = self.request.get("jgd")
		cache = self.request.get("cache")
		sid = get_sid_from_cookie()
		
		# preciso de lista de epocas, lista de competições, lista de clubes, lista de árbitros
		
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
				for elem in ['jogo','jogador','clube_tem_jogador','jogador_joga_jogo',
					'epoca','competicao','jornada']:
					cache = memcache.get(elem)
					if cache and cache['date'] > cacheresultados['date']:
						logging.info("Modelo '"+elem+"' tem elementos mais frescos ("+str(cache['date'])+") do que a cache desta procura ("+str(cacheresultados['date'])+")")
						cache_old = True
					
				if not cache_old:	
					logging.info ("Cache desta procura ("+str(cacheresultados['date'])+") ainda é fresca.")
				
			if not cacheresultados or cache_old:
			
				logging.info("Memcache para "+memcache_label+" é inexistente ou obsoleta. A gerar novos dados.")
				
				# jogos = None, cono está no início
				# devia fazer default a Jogos.all(), mas de notar que há épocas, competições e jornadas 
				# como critérios antecessores. Estes podem já refinar. 
				
# FILTRO POR ANTECESSORES (epoca, competicao, jornada)
# ou seja: estes filtros produzem a GqlQuery 'jogos'
					
				jogos = Jogo.all()
				
				
				# primeiro nível: 1
				if jog_realizados:
					if jog_realizados == "ja":
						jogos.filter("jog_data <= ", datetime.datetime.now())
					else:
						jogos.filter("jog_data > ", datetime.datetime.now())

				# primeiro nível: 2
				# if jog_epoca:
				# 	epoca = Epoca.get_by_id(int(jog_epoca))
				# 	jogos.filter("jog_epoca = ", epoca)
					
				# segundo nível: 2x2
				if jog_competicao:
					competicao = Competicao.get_by_id(int(jog_competicao))
					jogos.filter("jog_competicao = ", competicao)
					
				# segundo nível: 2x2
				# if jog_jornada_numero:
				# 	jornadas = Jornada.all().filter("jor_nome_curto = ",jog_jornada_numero).fetch(1000)
				# 	jogos.filter("jog_jornada in ", jornadas)
					
# FILTRO POR PROPRIEDADES (jogadores, golos, árbitros)
# ou seja: estes filtros FILTRAM a GqlQuery 'jogos'
		# jog_jogador = self.request.get("jog_jogador")
		# 
				if jog_clube1:
					clube = Clube.get_by_id(int(jog_clube1))
					jogos.filter("jog_clube1 = ", clube)
				
				if jog_clube2:
					clube = Clube.get_by_id(int(jog_clube2))
					jogos.filter("jog_clube2 = ", clube)
					
				if jog_arbitro:
					arbitro = Arbitro.get_by_id(int(jog_arbitro))
					jogos.filter("jog_arbitro = ", arbitro)
					
				if jog_golos_clube1:
					jogos.filter("jog_golos_clube1 = ", int(jog_golos_clube1))
					
				if jog_golos_clube2:
					jogos.filter("jog_golos_clube2 = ", int(jog_golos_clube2))
					
				if jog_jogador:
					jogador = Jogador.all().filter("jgd_nome = ", jog_jogador).get()
					if jogador:
						jogos_list = []
						for jjj in jogador.jgd_jogos:
							jogos_list.append(jjj.jjj_jogo.key())
						jogos.filter("__key__ in ",jogos_list)
				
			#	logging.info("Tenho jogos filtrados, count = "+str(jogos.count())+" (num_resultados = "+str(num_resultados)+")")
					
# FIM DA FILTRAGEM
					
# INÍCIO DA PAGINAÇÃO
					
				# now, let's prepare the pages
		#		jogos.order("-jog_numero_visitas")
				myPagedQuery = PagedQuery(jogos, int(num_resultados))
				myPagedQuery.order("-jog_data")

				#try:
				results_page = myPagedQuery.fetch_page(page_index)
				#except:
					# error = u"Lamentamos, mas essa combinação de pesquisas não podem ser satisfeitas:<UL><LI>Pesquisas só com épocas</LI><LI>Pesquisas com épocas e nomes de jogadores</LI></UL> Por favor, reformule os critérios para gerar uma pesquisa que o motor de busca consiga satisfazer."
				
					
				myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
					url_root=re.sub("pg=\d+", "", self.request.url), page_field="pg")	
				results_page_links = myLinks.get_links()
				results_total = jogos.count()
				
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
				"obj":"jogo",
				"panel":"pesquisa",
				"total":results_total,
				"nr":num_resultados
			}, 
			"content":[]
			}

			if results_page:
			
				count = (page_index - 1)*int(num_resultados)
			
				for jogo in results_page:
				
					count += 1
				
					resultados["content"].append({
					"nome":jogo.printjogo(),
					"logo1":jogo.jog_clube1.clu_link_logo,
					"logo2":jogo.jog_clube2.clu_link_logo,
					"data":jogo.jog_data.strftime("%Y-%m-%d"),
					"jornada":jogo.jog_jornada.jor_nome,
					"jornada_id":jogo.jog_jornada.key().id(),
					"competicao":jogo.jog_jornada.jor_competicao.cmp_nome_completo+" "+jogo.jog_jornada.jor_competicao.cmp_epoca.epo_nome,
					"competicao_id":jogo.jog_jornada.jor_competicao.key().id(),
					"id":jogo.key().id(),
					"click":count
					})

		flash_message = None
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(str(sid), namespace="flash")

		self.render_to_output('procurar_jogo.html', {
	#		"jog_epoca": jog_epoca,
			"jog_competicao": jog_competicao,
	#		"jog_jornada_numero": jog_jornada_numero,
			"jog_clube1": jog_clube1,
			"jog_clube2": jog_clube2,
			"jog_arbitro": jog_arbitro,
			"jog_golos_clube1": jog_golos_clube1,
			"jog_golos_clube2": jog_golos_clube2,
			"jog_jogador": jog_jogador,
			"num_resultados": num_resultados, 
			
			"flash":flash_message,
			
			# search results
			"results": resultados,
			"results_total": results_total,
			"results_page_links":results_page_links,

			# memcache stuff
			"clubes": listas.get_lista_clubes(),
			"epocas": listas.get_lista_epocas(), 
			"competicoes": listas.get_lista_competicoes(), 
			"arbitros": listas.get_lista_arbitros(), 
			"resultados": [15, 30, 40]
		})
		
