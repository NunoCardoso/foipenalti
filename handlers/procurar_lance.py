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

class ProcurarLance(MyHandler):
	
	def get(self):

		lances = None		
		num_resultados = self.request.get("nr")
		# critérios
	#	lan_epoca = self.request.get("epo")
		lan_competicao = self.request.get("cmp")
		#lan_jornada_numero = self.request.get("lan_jornada_numero")
		lan_clube1 = self.request.get("clu1")
		lan_clube2 = self.request.get("clu2")
		lan_arbitro = self.request.get("arb")
		lan_jogador = self.request.get("jgd")
		lan_classe = self.request.get("cla")
		cache = self.request.get("cache")
		sid =self.get_sid_from_cookie()
		
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
				for elem in ['lance','comentador_comenta_lance','jogador_em_lance']:
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
					
				lances = Lance.all()
				
				# primeiro nível: 2
				# if lan_epoca:
				# 	epoca = Epoca.get_by_id(int(lan_epoca))
				# 	lances.filter("lan_epoca = ", epoca)
					
				# segundo nível: 2x2
				if lan_competicao:
					competicao = Competicao.all().filter("cmp_nome = ",lan_competicao).get()
					lances.filter("lan_competicao = ", competicao)
					
				# segundo nível: 2x2
				# if lan_jornada_numero:
				# 	jornadas = Jornada.all().filter("jor_nome_curto = ",lan_jornada_numero).fetch(1000)
				# 	lances.filter("lan_jornada in ", jornadas)

				if lan_clube1:
					clube = Clube.get_by_id(int(lan_clube1))
					lances.filter("lan_clube1 = ", clube)
					
				if lan_clube2:
					clube = Clube.get_by_id(int(lan_clube2))
					lances.filter("lan_clube2 = ", clube)
					
				if lan_arbitro:
					arbitro = Arbitro.get_by_id(int(lan_arbitro))
					lances.filter("lan_arbitro = ", arbitro)
				
				if lan_classe:
					lances.filter("lan_classe = ", int(lan_classe))
				
				if lan_jogador:
					jogador = Jogador.all().filter("jgd_nome =",lan_jogador).get()
					jels = JogadorEmLance.all().filter("jel_jogador = ", jogador).fetch(1000)
					lance_list = []
					for j in jels:
						lance_list.append(j.jel_lance.key())
			
					lances.filter("__key__ in ", lance_list)
					
# FIM DA FILTRAGEM
					
# INÍCIO DA PAGINAÇÃO
					
				# now, let's prepare the pages
				myPagedQuery = PagedQuery(lances, int(num_resultados))
		#		myPagedQuery.order("-lan_data")
		#		try:
				results_page = myPagedQuery.fetch_page(page_index)
		#		except:
		#			error = u"Lamentamos, mas essa combinação de pesquisas não podem ser satisfeitas:<UL><LI>Pesquisas só com épocas</LI><LI>Pesquisas com épocas e nomes de jogadores</LI></UL> Por favor, reformule os critérios para gerar uma pesquisa que o motor de busca consiga satisfazer."

				
					
				myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
					url_root=re.sub("pg=\d+", "", self.request.url), page_field="pg")	
				results_page_links = myLinks.get_links()
				results_total = lances.count()
				
				memcache_label = self.request.path+":"+self.request.query_string
				
				logging.info("Setting new memcache data for "+memcache_label)
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
				"obj":"lance",
				"panel":"pesquisa",
				"total":results_total,
				"nr":num_resultados
			}, 
			"content":[]
			}

			if results_page:
			
				count = (page_index - 1)*int(num_resultados)
			
				for lance in results_page:
				
					count += 1
				
					prot = []
					for jel in lance.lan_jogadores:
						prot.append(jel.jel_jogador.jgd_nome)

					resultados["content"].append({
					"nome":lance.printlance(),
					"logo1":lance.lan_jogo.jog_clube1.clu_link_logo,
					"logo2":lance.lan_jogo.jog_clube2.clu_link_logo,
					"protagonistas":", ".join(prot),
					"data":lance.lan_jogo.jog_data.strftime("%Y-%m-%d"),
					"tipo":Lance.translation_classe[lance.lan_classe],
					"jogo":lance.lan_jogo.printjogo(),
					"jogo_id":lance.lan_jogo.jog_jornada.key().id(),
					"jornada":lance.lan_jogo.jog_jornada.jor_nome,
					"jornada_id":lance.lan_jogo.jog_jornada.key().id(),
					"competicao":lance.lan_jogo.jog_jornada.jor_competicao.cmp_nome_completo+" "+lance.lan_jogo.jog_jornada.jor_competicao.cmp_epoca.epo_nome,
					"competicao_id":lance.lan_jogo.jog_jornada.jor_competicao.key().id(),
					"id":lance.key().id(),
					"click":count
					})

		flash_message = None
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(str(sid), namespace="flash")
						
		self.render_to_output('procurar_lance.html', {

			## feedback of get variables
		#	"lan_epoca": lan_epoca,
			"lan_competicao": lan_competicao,
		#	"lan_jornada_numero": lan_jornada_numero,
			"lan_clube1": lan_clube1,
			"lan_clube2": lan_clube2,
			"lan_arbitro": lan_arbitro,
			"lan_classe": lan_classe,
			"lan_jogador": lan_jogador,
			"num_resultados": num_resultados, 
			
			"flash":flash_message,
			
			# search results
			"results": resultados,
			"results_total": results_total,
			"results_page_links":results_page_links,

			# memcache stuff
			"clubes": listas.get_lista_clubes(),
			"competicoes": listas.get_lista_competicoes(), 
			"tipos_lances": listas.get_lista_tipos_lances(),
			"arbitros": listas.get_lista_arbitros(), 
			"resultados": [15, 30, 40]
		})
		
