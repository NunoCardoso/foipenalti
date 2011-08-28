# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler

## gera listas simples quando invocado directamente por url /list,

urlpattern = re.compile('^(http:\/\/[^\/]*)\/admin\/([^\/]*)\/([^\?]*)(.*)$')

def rearrange_url_pager(objname, referrer, url):
		# o URL original pode vir de outros lados (ex: /admin/epoca/edit) e eu 
		# quero uma lista de, por exemplo. /admin/competicao/list.
		# eu preciso é de retirar os pg_{{objname}} e garantir que há um /list no final
		m = urlpattern.search(url)

		if m:
			host = m.group(1)
			objn = m.group(2)
			before_qm = m.group(3)
			qm_and_after = m.group(4)
			
			vars = None
			if qm_and_after and qm_and_after.startswith("?"):
				vars = qm_and_after[1:].split("&")
			
			vars2 = []
			if vars:
				for var in vars:
					if not var.startswith("pg_"):
						vars2.append(var)
				if referrer:
					vars2.append("referrer="+referrer)

			params = "&".join(vars2)
			if params:
				return host+"/admin/"+objname+"/list?"+params
			else:
				return host+"/admin/"+objname+"/list"
		
		return ""

def generate_basepath(objname, url):
		m = urlpattern.search(url)
		if m:
			host = m.group(1)
			objn = m.group(2)
			before_qm = m.group(3)
			qm_and_after = m.group(4)

			return host+"/admin/"+objname+"/list"
			
		return ""

class List(MyHandler):

	def get(self, objname):
		
		filter_field = self.request.get("filter_field")
		filter_needle = self.request.get("filter_needle")
		sid = self.request.get('sid')
		url = self.request.url

		# para quando se apaga registos...
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(sid, namespace="flash")

		# generate pager
		try:
			page_index = int(self.request.get("pg_"+objname,"1"))
		except ValueError:
			page_index = 1
			
		limit = 15

		id = None
		referrer = self.request.get("referrer")

		if self.request.get("id"):
			id = int(self.request.get("id"))
		objs = None
		
		if id:
			if referrer == "epoca" and objname == "competicao":
				objs = Epoca.get_by_id(id).epo_competicoes
			if referrer == "competicao" and objname == "jornada":
				objs = Competicao.get_by_id(id).cmp_jornadas
			if referrer == "competicao" and objname == "clube_joga_competicao":
				objs = ClubeJogaCompeticao.all().filter("cjc_competicao = ",  Competicao.get_by_id(id))
			if referrer == "jornada" and objname == "jogo":
				objs = Jornada.get_by_id(id).jor_jogos
			if referrer == "jogo" and objname == "lances":
				objs = Jogo.get_by_id(id).jog_lances
			if referrer == "jogo" and objname == "jogador_joga_jogo":
				objs = JogadorJogaJogo.all().filter("jjj_jogo = ",  Jogo.get_by_id(id))
			if referrer == "lance" and objname == "comentador_comenta_lance":
				objs = ComentadorComentaLance.all().filter("ccl_lance = ",  Lance.get_by_id(id))
			if referrer == "lance" and objname == "jogador_em_lance":
				objs = JogadorEmLance.all().filter("jel_lance = ",  Lance.get_by_id(id))
			if referrer == "jogador" and objname == "clube_tem_jogador":
				objs = ClubeTemJogador.all().filter("ctj_jogador = ",  Jogador.get_by_id(id))
		
		html = self.gera_lista({
			"objs":objs, 
			"objname":objname, 
			"filter_field":filter_field,
			"filter_needle":filter_needle, 
			"url":url, 
			"referrer":referrer,
			"page_index":page_index, 
			"limit":limit,
			"flash":flash_message})
		
		
		self.response.out.write(html)
	
	# objs: envia os objs para iterar
	# objname: o tipo de objectos que se está a iterar
	# filter_field, filter_needle: filtros para estes objextos
	# url: O URL que invocou a tabela (é preciso algumas variáveis get, como um id referrer)
	# obj_referrer: o tipo de objecto referrer. A tabela pose ser de objectos restringidos
	# a um id, portanto há que reconstruir a lista de objs.
	# page_index, limir
	
	def gera_lista(self, params):
		
		objs = params["objs"]
		objname = params["objname"]

		filter_field = None
		filter_needle = None
		url = None
		referrer = None
		page_index = None
		limit = None
		flash = None
		
		if params.has_key("filter_field"):
			filter_field = params["filter_field"]
		if params.has_key("filter_needle"):
			filter_needle = params["filter_needle"]
		if params.has_key("url"):
			url = params["url"]
		if params.has_key("referrer"):
			referrer = params["referrer"]
		if params.has_key("page_index"):
			page_index = params["page_index"]
		if params.has_key("limit"):
			limit = params["limit"]
		if params.has_key("flash"):
			flash = params["flash"]
		
#############
### EPOCA ###
#############

		omit = []
		myPagedQuery = None

		
		if objname == "epoca":
			if objs == None:
				objs = Epoca.all()
			fields = Epoca.fields

			# nome = string, ano_inicio e ano_fim = int
			if filter_field:
				if filter_field == "epo_data_inicio" or filter_field == "epo_data_fim":
					objs.filter(filter_field+" = ", datetime.datetime.strptime(filter_needle, "%Y-%m-%d").date())
				else: # ano_fim, ano_inicio => int
					objs.filter(filter_field+" = ", filter_needle)
			
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-epo_ultima_alteracao')

##################
### COMPETICAO ###
##################
		
		elif objname == "competicao":
			if objs == None:
				objs = Competicao.all()
			fields = Competicao.fields
			omit = ['cmp_epoca']
			
			# tudo é string, excepto cmp_epoca
			if filter_field:
				if filter_field == "cmp_epoca":
					
					objs.filter(filter_field+" = ", Epoca.all().filter("epo_nome = ", filter_needle).get() )
				elif filter_field == "cmp_numero_jornadas" or \
					filter_field.startswith("cmp_lugares_"):
					
					objs.filter(filter_field+" = ", int(filter_needle))	
				else:
					objs.filter(filter_field+" = ", filter_needle)	
					
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-cmp_ultima_alteracao')

###############
### JORNADA ###
###############
		
		elif objname == "jornada":
		
			if objs == None:
				objs = Jornada.all()
			fields = Jornada.fields
			omit = ['jor_epoca','jor_competicao']
			
			# tudo é string, excepto jor_competicao
			if filter_field:
				
				if filter_field == "jor_epoca":
					epoca = Epoca.all().filter("epo_nome = ",filter_needle).get()
					objs.filter(filter_field+" = ", epoca)

				elif filter_field == "jor_competicao":
					competicao = Competicao.all().filter("cmp_nome = ", filter_needle).get()					
					objs.filter(filter_field+" = ", competicao)

				elif filter_field == "jor_ordem":
					objs.filter(filter_field+" = ", int(filter_needle))

				elif filter_field == "jor_data":
					objs.filter(filter_field+" = ", datetime.datetime.strptime(filter_needle, "%Y-%m-%d").date())

				else:
					objs.filter(filter_field+" = ", filter_needle)	
			
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-jor_ultima_alteracao')	

############
### JOGO ###
############
			
		elif objname == "jogo":
			if objs == None:
				objs = Jogo.all()
			fields = Jogo.fields
			omit = ['jog_epoca','jog_competicao','jog_jornada']
			
			# tem: Jornada, date, Clube, Arbitros, int(golos), string
			if filter_field:
				
				# Epoca
				if filter_field == "jog_epoca":
					epoca = Epoca.all().filter("epo_nome = ",filter_needle).get()
					objs.filter(filter_field+" = ", epoca)

				# Competicao
				elif filter_field == "jog_competicao":
					competicao = Competicao.all().filter("cmp_nome = ", filter_needle).get()					
					objs.filter(filter_field+" = ", competicao)

				# Jornada
				if filter_field == "jog_jornada":
					jornada = Jornada.all().filter("jor_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", jornada)
				
				# Clubes
				elif filter_field == "jog_clube1" or filter_field == "jog_clube2" or \
				 filter_field == "jog_clube_beneficiado" or filter_field == "jog_clube_prejudicado":
					clube = Clube.all().filter("clu_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", clube)

				# Clubes.key
				elif filter_field == "jog_clubes":
					clube = Clube.all().filter("clu_nome = ", filter_needle).get()
					objs.filter(filter_field+" IN ", clube.key())
			
				# data
				elif filter_field == "jor_data":
					objs.filter(filter_field+" = ", datetime.datetime.strptime(filter_needle, "%Y-%m-%d %H:%M"))

				# Arbitro
				elif filter_field == "jog_arbitro":
					objs.filter(filter_field+" = ", 
						Arbitro.all().filter("arb_nome = ", filter_needle).get() )

				# ints 
				elif filter_field == "jog_golos_clube1" or filter_field == "jog_golos_clube2" or \
				 filter_field == "jog_golos_virtuais_clube1" or filter_field == "jog_golos_virtuais_clube2" or \
				 filter_field == "jog_influencia_arbitro" or filter_field == "jog_julgamento_arbitro":
					objs.filter(filter_field+" = ", int(filter_needle)) 

				# floats 
				elif filter_field == "jog_icc" or filter_field == "jog_ica":
					objs.filter(filter_field+" = ", float(filter_needle)) 

				else:
					objs.filter(filter_field+" = ", filter_needle) 
			
			#omit = "jog_link_videos"
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-jog_ultima_alteracao')
	
#############
### LANCE ###
#############			
			
		elif objname == "lance":
			if objs == None:
				objs = Lance.all()
			fields = Lance.fields
			omit = ['lan_epoca','lan_competicao','lan_jornada','lan_ultima_alteracao','lan_jogo']
			
			if filter_field:
				
				# Epoca
				if filter_field == "lan_epoca":
					epoca = Epoca.all().filter("epo_nome = ",filter_needle).get()
					objs.filter(filter_field+" = ", epoca)

				# Competicao
				elif filter_field == "lan_competicao":
					competicao = Competicao.all().filter("cmp_nome = ", filter_needle).get()					
					objs.filter(filter_field+" = ", competicao)

				# Jornada
				if filter_field == "lan_jornada":
					jornada = Jornada.all().filter("jor_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", jornada)

				# JOGO
				if filter_field == "lan_jogo":
					jogo = Jogo.all().filter("jog_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", jogo)
				
				# Clubes
				elif filter_field == "lan_clube1" or filter_field == "lan_clube2" or \
				 filter_field == "lan_clube_beneficiado" or filter_field == "lan_clube_prejudicado":
					clube = Clube.all().filter("clu_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", clube)

				# Clubes.key
				elif filter_field == "lan_clubes":
					clube = Clube.all().filter("clu_nome = ", filter_needle).get()
					objs.filter(filter_field+" IN ", clube.key())

				# data
				elif filter_field == "lan_data":
					objs.filter(filter_field+" = ", datetime.datetime.strptime(filter_needle, "%Y-%m-%d %H:%M"))

				# Arbitro
				elif filter_field == "lan_arbitro":
					objs.filter(filter_field+" = ", 
						Arbitro.all().filter("arb_nome = ", filter_needle).get() )

				# int
				elif filter_field == "lan_numero" or filter_field == "lan_minuto" or \
					filter_field == "lan_classe" or filter_field == "lan_causa" or \
					filter_field == "lan_apitado" or filter_field == "lan_consequencia" or \
					filter_field == "lan_julgamento_arbitro":

					objs.filter(filter_field+" = ", int(filter_needle))
				else:
					objs.filter(filter_field+" = ", filter_needle)
					
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-lan_ultima_alteracao')

#############
### CLUBE ###
#############
		
		elif objname == "clube":
			
			if objs == None:
				objs = Clube.all()
			fields = Clube.fields
			
			# tudo string fields
			if filter_field:
				objs.filter(filter_field+" = ", filter_needle)
			
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-clu_ultima_alteracao')
			
#############
## JOGADOR ##
#############

		elif objname == "jogador":
			if objs == None:
				objs = Jogador.all()
			fields = Jogador.fields
			
			# tudo string fields
			if filter_field:
				if filter_field == "jgd_clube_actual":
					objs.filter(filter_field+" = ", Clube.all().filter("clu_nome = ", filter_needle).get())
				elif filter_field == "jgd_numero":
					objs.filter(filter_field+" = ", int(filter_needle))
				else:
					objs.filter(filter_field+" = ", filter_needle)

			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-jgd_ultima_alteracao')

#############
## ARBITRO ##
#############
			
		elif objname == "arbitro":
			if objs == None:
				objs = Arbitro.all()
			fields = Arbitro.fields
			
			# só tem string
			if filter_field:
				objs.filter(filter_field+" = ", filter_needle)
				
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-arb_ultima_alteracao')
			
################
## COMENTADOR ##
################
			
		elif objname == "comentador":
			if objs == None:
				objs = Comentador.all()
			fields = Comentador.fields
			
			# strings e Fonte
			if filter_field:
				
				if filter_field == "com_fonte":
					objs.filter(filter_field+" = ", 
						Fonte.all().filter("fon_nome = ", filter_needle).get() )
				else:
					objs.filter(filter_field+" = ", filter_needle)	
					
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-com_ultima_alteracao')
			
###########
## FONTE ##
###########
			
		elif objname == "fonte":
			if objs == None:
				objs = Fonte.all()
			fields = Fonte.fields
			
			# só strings 
			if filter_field:
				
				objs.filter(filter_field+" = ", filter_needle)
				
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-fon_ultima_alteracao')

#######################
## CLUBE_TEM_JOGADOR ##
#######################
		
		elif objname == "clube_tem_jogador":
			if objs == None:
				objs = ClubeTemJogador.all()
			fields = ClubeTemJogador.fields
			
			# Clube, Jogador, lista de epocas(key), numero (int)
			if filter_field:
				
				if filter_field == "ctj_clube":
					clube = Clube.all().filter("clu_nome = :1 ", filter_needle).get()
					objs.filter(filter_field+" = ", clube)
				
				elif filter_field == "ctj_jogador":
					objs.filter(filter_field+" = ", 
						Jogador.all().filter("jgd_nome = ", filter_needle).get() )
				
				# é uma Key
				elif filter_field == "ctj_epocas":
					epoca = Epoca.all().filter("epo_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", epoca.key())
					
				# int
				elif filter_field == "ctj_numero":
					objs.filter(filter_field+" = ", int(filter_needle))
				
			myPagedQuery = PagedQuery(objs, limit)
			
###########################
## CLUBE_JOGA_COMPETICAO ##
###########################
			
		elif objname == "clube_joga_competicao":
			if objs == None:
				objs = ClubeJogaCompeticao.all()
			fields = ClubeJogaCompeticao.fields
			
			# Clube, Competicao 
			if filter_field:
				if filter_field == "cjc_clube":
					clube = Clube.all().filter("clu_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", clube)
				
				elif filter_field == "cjc_competicao":
					competicao = Competicao.gql('cmp_nome = ', filter_needle).get()
					objs.filter(filter_field+" = ", competicao )
			
			myPagedQuery = PagedQuery(objs, limit)

#######################
## JOGADOR_JOGA_JOGO ##
#######################

		elif objname == "jogador_joga_jogo":
			if objs == None:
				objs = JogadorJogaJogo.all()
			fields = JogadorJogaJogo.fields
			limit = 30

			# Jogador, Jogo, List(ints) - amarelos, vermelhos golos, ints (substituições)
			if filter_field:
				
				if filter_field == "jjj_jogador":
					objs.filter(filter_field+" = ", 
						Jogador.all().filter("jgd_nome = ", filter_needle).get() )
				
				elif filter_field == "jjj_jogo":
					jogo = Jogo.all().filter("jog_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", jogo)
				
				else:
					# acho que lista(int) e int levam com o mesmo filtro... digo eu...
					objs.filter(filter_field+" = ", int(filter_needle))
				
			myPagedQuery = PagedQuery(objs, limit)

##############################
## COMENTADOR_COMENTA_LANCE ##
##############################			
			
		elif objname == "comentador_comenta_lance":
			if objs == None:
				objs = ComentadorComentaLance.all()
			fields = ComentadorComentaLance.fields
			
			# ignorar descrição. Há Comentador, há Lance,há int(decisao)
			if filter_field:
				if filter_field == "ccl_comentador":
					objs.filter(filter_field+" = ", 
						Comentador.all().filter("com_nome = ", filter_needle).get() )
				
				elif filter_field == "ccl_lance":
					lance = Lance.all().filter("lan_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", lance)
				
				elif filter_field == "ccl_decisao":
					objs.filter(filter_field+" = ", int(filter_needle))
					
			myPagedQuery = PagedQuery(objs, limit)

######################
## JOGADOR_EM_LANCE ##
######################			
		
		elif objname == "jogador_em_lance":
			if objs == None:
				objs = JogadorEmLance.all()
			fields = JogadorEmLance.fields
			
			#jogador, lance, papel
			if filter_field:
				if filter_field == "jel_jogador":
					objs.filter(filter_field+" = ", 
						Jogador.all().filter("jgd_nome = ", filter_needle).get() )
			
				elif filter_field == "jel_lance":
					lance = Lance.all().filter("lan_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", lance)
					
				else:
					objs.filter(filter_field+" = ", filter_needle)
				
			myPagedQuery = PagedQuery(objs, limit)

##########################		
### ACUMULADOR JORNADA ###
##########################		

		elif objname == "acumulador_jornada":
			if objs == None:
				objs = AcumuladorJornada.all()
			fields = AcumuladorJornada.fields
			omit = ['acuj_epoca','acuj_competicao','acuj_content']
			
			#jogador, lance, papel
			if filter_field:

				if filter_field == "acuj_epoca":
				# Epoca
					epoca = Epoca.all().filter("epo_nome = ",filter_needle).get()
					objs.filter(filter_field+" = ", epoca)

				# Competicao
				elif filter_field == "acuj_competicao":
					competicao = Competicao.all().filter("cmp_nome = ", filter_needle).get()					
					objs.filter(filter_field+" = ", competicao)

				# Jornada
				if filter_field == "acuj_jornada":
					jornada = Competicao.all().filter("jor_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", jornada)

				elif filter_field == "acuj_versao":
					objs.filter(filter_field+" = ", int(filter_needle))	

				else:
					objs.filter(filter_field+" = ", filter_needle)	
			
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-acuj_date')

#############################		
### ACUMULADOR COMPETICAO ###
#############################	

		elif objname == "acumulador_competicao":
			if objs == None:
				objs = AcumuladorCompeticao.all()
			fields = AcumuladorCompeticao.fields
			omit = ['acuc_epoca','acuc_content']
			
			#jogador, lance, papel
			if filter_field:
				if filter_field == "acuc_epoca":
				# Epoca
					epoca = Epoca.all().filter("epo_nome = ",filter_needle).get()
					objs.filter(filter_field+" = ", epoca)

				# Competicao
				elif filter_field == "acuc_competicao":
					competicao = Competicao.all().filter("cmp_nome = ", filter_needle).get()					
					objs.filter(filter_field+" = ", competicao)


				elif filter_field == "acuc_versao":
					objs.filter(filter_field+" = ", int(filter_needle))	
				else:
					objs.filter(filter_field+" = ", filter_needle)	
			
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-acuc_date')
		
########################		
### ACUMULADOR EPOCA ###
########################

		elif objname == "acumulador_epoca":
			if objs == None:
				objs = AcumuladorEpoca.all()
			fields = AcumuladorEpoca.fields
			omit = ['acue_content']
			
			#jogador, lance, papel
			if filter_field:
				if filter_field == "acue_epoca":
					epoca = Epoca.all().filter("epo_nome = ", filter_needle).get()
					objs.filter(filter_field+" = ", epoca)

				elif filter_field == "acue_versao":
					objs.filter(filter_field+" = ", int(filter_needle))	
				else:
					objs.filter(filter_field+" = ", filter_needle)	
			
			myPagedQuery = PagedQuery(objs, limit)
			myPagedQuery.order('-acue_date')
			
		# ok, now let's page results
		
		myResults = None
		
		if myPagedQuery:
			
			myResults = myPagedQuery.fetch_page(page_index)
			myLinks = PageLinks(page=page_index, page_count=myPagedQuery.page_count(), 
				url_root=rearrange_url_pager(objname, referrer, url), page_field="pg_"+objname)	
			page_navigation_links = myLinks.get_links()
		
		template_path = os.path.join(config.APP_ROOT_DIR, "templates", "admin", "list.html")
		
		return template.render(template_path, {
			'objs': myResults,
			'flash':flash,
			'objname': objname,
			'number': objs.count() if objs else 0,
			'filter_field':filter_field,
			'filter_needle':filter_needle,
			'fields': fields,
			'omit': omit,
			'pager': page_navigation_links,
			'page_index':page_index,
			'basepath':generate_basepath(objname, url)
		})
