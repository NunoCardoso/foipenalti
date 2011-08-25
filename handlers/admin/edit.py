# -*- coding: utf-8 -*-

#### VERSAO 5: Falta adicionar os multiple_new e multiple_edit onde necessário ####

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 
import urllib 

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler
from list import List

from lib import listas

class Edit(MyHandler):
	
	def get(self, objname):
		
		id = int(self.request.get('id'))
		tab = self.request.get('tab')
		
		flash_message = memcache.get("flash")
		if flash_message:
			memcache.delete("flash")
		
		# há que forçar o encoding do & também
		raw_referer = "/admin/"+objname+"/"
		if os.environ.has_key('HTTP_REFERER'):
			raw_referer = re.sub("&","%38",urllib.quote_plus(os.environ['HTTP_REFERER']))
		
		values = {}
		omit_properties = [] # propriedades do objecto que não precisam de ser impressas e prontas para ser editadas

#############################
######## EDIT EPOCA #########
#############################		

		if objname == "epoca":
			
			obj = Epoca.get_by_id(id)
			
			#### DEPENDENTE 1: COMPETICAO ####
			objname1 = "competicao"
			
			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1
				
			limit1 = 10
			
			# para editar batch de competições
			objs = []
			for competicao in obj.epo_competicoes:
				objs.append(competicao)
			
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {

				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Epoca.fields, 'tab':tab,

				# editar this: editar época
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				}),
				
				# listar dependente 1: competições desta época
				'list1': List().gera_lista({
					"objs":obj.epo_competicoes, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novos dependentes 1: novas múltiplas competições anexadas a esta época
				'mnew1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True,
						'this_id':'epo_id', 'obj':obj, "objname":objname1, 
						'howmany':10
				}),

				# editar dependentes 1: editar múltiplas competições anexadas a esta época
				'medit1':self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'multiple_edit':True, 'obj':obj, 'objs':objs, "objname":objname1, 
						'howmany':len(objs)
				})
				
			})
			
##################################
######## EDIT COMPETICAO #########		
##################################

		elif objname == "competicao":
			obj = Competicao.get_by_id(id)
			
			#### DEPENDENTE 1: JORNADAS ####
			objname1 = "jornada"
			objs1 = []
			for o in obj.cmp_jornadas:
				objs1.append(o)

			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1
			limit1 = 30

			#### DEPENDENTE 2: CLUBE JOGA COMPETICAO ####
			objname2 = "clube_joga_competicao"
			objs2 = []
			
			ob2 = ClubeJogaCompeticao.all().filter("cjc_competicao = ", obj)
			for o in ob2:
				objs2.append(o)
				
			try:
				page_index2 = int(self.request.get("pg_"+objname2,"1"))
			except ValueError:
				page_index2 = 1
			limit2 = 30

			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Competicao.fields, 'tab':tab,

				# editar this: editar competição
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj,
						'epocas':listas.get_lista_epocas()
				}),
				
				# listar dependente 1: jornadas desta competição
				'list1': List().gera_lista({
					"objs":obj.cmp_jornadas, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novas jornadas anexada a esta competicao
				'mnew1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, "objname":objname1, 
						'this_id':'cmp_id', 'obj':obj, 'howmany':10
				}),
				
				# editar dependentes 1: editar múltiplas jornadas anexadas a esta competição
				'medit1':self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'multiple_edit':True, "objname":objname1, 
						'obj':obj, 'objs':objs1, 'howmany':len(objs1)
				}),
				
				# listar dependente 2: clubes desta competição
				'list2': List().gera_lista({
					"objs":ob2, "objname":objname2, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index2, "limit":limit2
				}),
				
				# novos dependentes 2: novos clubes anexados a esta competicao
				'mnew2': self.render_subdir("admin", 'obj_%s_multiple.html' % objname2, {
						'new_for_parent_id':True, "objname":objname2, 
						'this_id':'cmp_id', 'obj':obj, 'howmany':10,
						'clubes':listas.get_lista_clubes(),
						'competicoes':listas.get_lista_competicoes()
				}),
				
				# editar dependentes 1: editar múltiplos clubes anexadas a esta competicao
				'medit2':self.render_subdir("admin", 'obj_%s_multiple.html' % objname2, {
						'multiple_edit':True, 'obj':obj, 'objs':objs2, 
						'this_id':'cmp_id','howmany':len(objs2), "objname":objname2, 
						'clubes':listas.get_lista_clubes(),
						'competicoes':listas.get_lista_competicoes()
				})
			})

###############################
######## EDIT JORNADA #########
###############################
		
		elif objname == "jornada":
			
			obj = Jornada.get_by_id(id)

			#### DEPENDENTE 1: JOGOS ####
			objname1 = 'jogo'
			objs1 = []
			for o in obj.jor_jogos:
				objs1.append(o)
			
			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1
			
			limit1 = 10
			
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Jornada.fields, 'tab':tab,

				# editar this: editar jornada
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj,
						'competicoes':listas.get_lista_competicoes()
				}),
				
				# listar dependente 1: jogos desta jornada
				'list1': List().gera_lista({
					"objs":obj.jor_jogos, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos jogos anexados a esta jornada
				'mnew1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, "objname":objname1, 
						'this_id':'jor_id', 'obj':obj, 'howmany':10,
						'clubes':listas.get_lista_clubes(),
						'arbitros':listas.get_lista_arbitros(), # para select com árbitros,
						'tacticas':listas.get_lista_tacticas()
				}),
				
				# editar dependentes 1: editar múltiplos jogos anexadas a esta jornada
				'medit1':self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'multiple_edit':True, 'obj':obj, 'objs':objs1, 
						'howmany':len(objs1), 
						'clubes':listas.get_lista_clubes(),
						'arbitros':listas.get_lista_arbitros(), # para select com árbitros,
						'tacticas':listas.get_lista_tacticas()
				})
			})

############################
######## EDIT JOGO #########
############################

		elif objname == "jogo":
			
			obj = Jogo.get_by_id(id)

			# DEPENDENTE 1
			objname1 = 'jogador_joga_jogo'
			objs1 = []

			for o in obj.jog_jogadores:
				objs1.append(o)

			# DEPENDENTE 2
			objname2 = 'lance'
			objs2 = []
			for o in obj.jog_lances:
				objs2.append(o)

			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1

			try:
				page_index2 = int(self.request.get("pg_"+objname2,"1"))
			except ValueError:
				page_index2 = 1
			
			limit1 = 30
			limit2 = 10		
	
			# vamos buscas jogadores dos dois clubes e colocar na select box
			# aproveitar e retirar aqueles que já lá estão
			todos_jogadores = []
			jogadores_clube1 = []
			jogadores_clube2 = []
			
			for jogador in obj.jog_jogadores:
				todos_jogadores.append(jogador.jjj_jogador)
				if jogador.jjj_clube == obj.jog_clube1:
					jogadores_clube1.append(jogador)
						
				else:
					if jogador.jjj_clube == obj.jog_clube2:
						jogadores_clube2.append(jogador)	

			todos_jogadores_clube1 = Jogador.all().filter("jgd_clube_actual = ", obj.jog_clube1).fetch(1000)
			todos_jogadores_clube2 = Jogador.all().filter("jgd_clube_actual = ", obj.jog_clube2).fetch(1000)
			
			# JOGADOR
			todos_jogadores_clube1 = sorted(todos_jogadores_clube1, cmp=lambda x,y: cmp(x.jgd_nome, y.jgd_nome))
			todos_jogadores_clube2 = sorted(todos_jogadores_clube2, cmp=lambda x,y: cmp(x.jgd_nome, y.jgd_nome))
			todos_jogadores = sorted(todos_jogadores, cmp=lambda x,y: cmp(x.jgd_nome, y.jgd_nome))
			
			# JJJ
			jogadores_clube1 = sorted(jogadores_clube1, cmp=lambda x,y: cmp(x.jjj_jogador.jgd_nome, y.jjj_jogador.jgd_nome))
			jogadores_clube2 = sorted(jogadores_clube2, cmp=lambda x,y: cmp(x.jjj_jogador.jgd_nome, y.jjj_jogador.jgd_nome))
			
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Jogo.fields, 'tab':tab,

				# editar this: editar jogo
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj,
						'clubes':listas.get_lista_clubes(),
						'arbitros':listas.get_lista_arbitros(), # para select com árbitros,
						'tacticas':listas.get_lista_tacticas()
				}),
				
				# listar dependente 1: jjjs deste jogo
				'list1': List().gera_lista({
					"objs":obj.jog_jogadores, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos jjj anexados a este jogo
				'mnew1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, "objname":objname1, 
						'this_id':'jog_id', 'obj':obj, 'howmany':28, 
						# parâmetros extra
						'jogadores_clube1':todos_jogadores_clube1,
						'jogadores_clube2':todos_jogadores_clube2,
						'clubes':listas.get_lista_clubes(),
						'posicoes':listas.get_lista_posicoes()
				}),

				# editar dependentes 1: editar múltiplos jjj anexadas a este jogo
				
				# on the render, use jjj_clube1 and jjj_clube2 instead of obj.jog_jogadores
				# because they are ordered.
				'medit1':self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'multiple_edit':True, 'obj':obj, 'objs':objs1, 
						'howmany':len(objs1),  "objname":objname1, 
						# parâmetros extra
						'jogadores_clube1':todos_jogadores_clube1,
						'jogadores_clube2':todos_jogadores_clube2,
						'clubes':listas.get_lista_clubes(),
						'posicoes':listas.get_lista_posicoes(),
						'jjj_clube1':jogadores_clube1,
						'jjj_clube2':jogadores_clube2
				}),
				
				# listar dependente 2: lances deste jogo
				'list2': List().gera_lista({
					"objs":obj.jog_lances, "objname":objname2, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index2, "limit":limit2
				}),
				
				# novos dependentes 2: novos lances associados a este jogo
				'mnew2': self.render_subdir("admin", 'obj_%s_multiple.html' % objname2, {
						'new_for_parent_id':True, "objname":objname2, 
						'this_id':'jog_id', 'obj':obj, 'howmany':10,
						#parâmetros extra
						'jogadores_clube1':todos_jogadores_clube1,
						'jogadores_clube2':todos_jogadores_clube2,
						'jogadores':todos_jogadores,
						'clubes':listas.get_lista_clubes(),
						'tipos_lances':listas.get_lista_tipos_lances(),
						'tipos_jels':listas.get_lista_tipos_jels(),
						'comentadores':listas.get_lista_comentadores()
				}),
				
				# editar dependentes 1: editar múltiplos lances anexadas a este jogo
				'medit2':self.render_subdir("admin", 'obj_%s_multiple.html' % objname2, {
						'multiple_edit':True, 'obj':obj, 'objs':objs2, 
						'howmany':len(objs2),  "objname":objname2, 
						'jogadores_clube1':todos_jogadores_clube1,
						'jogadores_clube2':todos_jogadores_clube2,
						'jogadores':todos_jogadores,
						'clubes':listas.get_lista_clubes(),
						'tipos_lances':listas.get_lista_tipos_lances(),
						'tipos_jels':listas.get_lista_tipos_jels(),
						'comentadores':listas.get_lista_comentadores()
				}),
			})

#############################
######## EDIT LANCE #########
#############################
			
		elif objname == "lance":
			
			obj = Lance.get_by_id(id)

			# DEPENDENTE 1	
			objname1 = 'comentador_comenta_lance'
			objs1 = []
			for o in ComentadorComentaLance.all().filter("ccl_lance = ", obj):
				objs1.append(o)

			# DEPENDENTE 2			
			objname2 = 'jogador_em_lance'
			objs2 = []
			for o in JogadorEmLance.all().filter("jel_lance = ", obj):
				objs2.append(o)

			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1

			try:
				page_index2 = int(self.request.get("pg_"+objname2,"1"))
			except ValueError:
				page_index2 = 1
						
			limit1 = 10
			limit2 = 10
			
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Lance.fields, 'tab':tab,

				# editar this: editar lance
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj, 'objname':objname,
						'tipos_lances':listas.get_lista_tipos_lances()
				}),
				
				# listar dependente 1: ccls deste lance
				'list1': List().gera_lista({
					"objs":obj.lan_comentadores, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos ccls anexados a este lance
				'mnew1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, 'objname':objname1,
						'this_id':'lan_id', 'obj':obj, 'howmany':3,
						# parâmetros extra
						'comentadores':listas.get_lista_comentadores()
				}),

				# editar dependentes 1: editar múltiplos ccls anexadas a este lance
				'medit1':self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'multiple_edit':True, 'obj':obj, 'objs':objs1, 
						'this_id':'lan_id','howmany':len(objs1), 'objname':objname1,
						'comentadores':listas.get_lista_comentadores()
				}),
				
				# listar dependente 2: comentadores deste lance
				'list2': List().gera_lista({
					"objs":obj.lan_jogadores, "objname":objname2, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index2, "limit":limit2
				}),
				
				# novo dependente 2: novos ccls associados a este lance
				'mnew2': self.render_subdir("admin", 'obj_%s_multiple.html' % objname2, {
						'new_for_parent_id':True, 'objname':objname2,
						'this_id':'lan_id', 'obj':obj, 'howmany':3,
						#parâmetros extra
						'tipos_jels':listas.get_lista_tipos_jels(),
				}),
				# editar dependentes 1: editar múltiplos ccls anexadas a este lance
				'medit2':self.render_subdir("admin", 'obj_%s_multiple.html' % objname2, {
						'multiple_edit':True, 'obj':obj, 'objs':objs2, 
						'this_id':'lan_id','howmany':len(objs2),'objname':objname2,
						'tipos_jels':listas.get_lista_tipos_jels(),
				}),
			})

#############################
######## EDIT CLUBE #########
#############################
		
		elif objname == "clube":
			
			obj = Clube.get_by_id(id)
						
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Clube.fields, 'tab':tab,

				# editar this: editar clube
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj, 'objname': objname
				}),
			})

##############################
####### EDIT JOGADOR #########
##############################

		elif objname == "jogador":
		
			obj = Jogador.get_by_id(id)

			#dependente 1
			objname1 = 'clube_tem_jogador'
			objs1 = []
			for o in ClubeTemJogador.all().filter("ctj_jogador = ", obj):
				objs1.append(o)
			
			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1

			limit1 = 20
			
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Jogador.fields, 'tab':tab,

				# editar this: editar jogador
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj,
						'posicoes':listas.get_lista_posicoes(),
						'epocas':listas.get_lista_epocas(),
						'clubes':listas.get_lista_clubes()

				}),
				
				# listar dependente 1: clubes deste jogador
				'list1': List().gera_lista({
					"objs":obj.jgd_clubes, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos CTJs anexados a este jogador
				'mnew1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True,
						'this_id':'jgd_id', 'obj':obj,
						'howmany':10, "objname":objname1, 
						'epocas':listas.get_lista_epocas(),
						'clubes':listas.get_lista_clubes()
				}),
				
				# edit dependente 1: editar CTJs anexados a este jogador
				'medit1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'multiple_edit':True, 'obj':obj, 'objs':objs1, 
						'this_id':'jgd_id','howmany':len(objs1), 'objname':objname1,
						'epocas':listas.get_lista_epocas(),
						'clubes':listas.get_lista_clubes()
				}),
				
			})

##############################
####### EDIT ARBITRO #########
##############################
		
		elif objname == "arbitro":
			
			obj = Arbitro.get_by_id(id)

			# DEPENDENCIA 1: JOGOS
			objname1 = 'jogo'

			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1
			
			limit1 = 10

			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Arbitro.fields, 'tab':tab,

				# editar this: editar árbitro
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				}),
				
				# listar dependente 1: jogos deste árbitro
				'list1': List().gera_lista({
					"objs":obj.arb_jogos, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos jogos anexados a este árbitro
				'new1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, "objname":objname1, 
						'this_id':'arb_id', 'obj':obj
				})
			})

#################################
####### EDIT COMENTADOR #########
#################################

		elif objname == "comentador":
			
			obj = Comentador.get_by_id(id)
			# DEPENDENTE 1
			objname1 = 'comentador_comenta_lance'
			
			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1
			
			limit1 = 10

			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Comentador.fields, 'tab':tab,

				# editar this: editar comentador
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				}),
				
				# listar dependente 1: lances deste comentador
				'list1': List().gera_lista({
					"objs":obj.com_lances, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos lances anexados a este comentador
				'new1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, "objname":objname1, 
						'this_id':'com_id', 'obj':obj
				})
			})		

############################
####### EDIT FONTE #########
############################

		elif objname == "fonte":
			
			obj = Fonte.get_by_id(id)

			# DEPENDENCIA1: 
			objname1 = 'comentador'
			
			try:
				page_index1 = int(self.request.get("pg_"+objname1,"1"))
			except ValueError:
				page_index1 = 1
			
			limit1 = 10

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': Fonte.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				}),
				
				# listar dependente 1: comentadores desta fonte
				'list1': List().gera_lista({
					"objs":obj.fon_comentadores, "objname":objname1, 
					"filter_field":None, "filter_needle":None, 
					"url":self.request.url, "referrer":objname,
					"page_index":page_index1, "limit":limit1
				}),
				
				# novo dependente 1: novos comentadores anexados a esta fonte
				'new1': self.render_subdir("admin", 'obj_%s_multiple.html' % objname1, {
						'new_for_parent_id':True, "objname":objname1, 
						'this_id':'fon_id', 'obj':obj
				})
			})		
			

######## EDIT clube_tem_jogador #########
			
		elif objname == "clube_tem_jogador":
			obj = ClubeTemJogador.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': ClubeTemJogador.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})
				
######## EDIT clube_joga_competicao #########
				
		elif objname == "clube_joga_competicao":
			obj = ClubeJogaCompeticao.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': ClubeJogaCompeticao.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})

######## EDIT jogador_joga_jogo #########
						
		elif objname == "jogador_joga_jogo":
			obj = JogadorJogaJogo.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': JogadorJogaJogo.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})

######## EDIT comentador_comenta_lance #########

		elif objname == "comentador_comenta_lance":
			obj = ComentadorComentaLance.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': ComentadorComentaLance.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})

######## EDIT jogador_em_lance #########

		elif objname == "jogador_em_lance":
			obj = JogadorEmLance.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': JogadorEmLance.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})
		
######## EDIT acumulador jornada #########
			
		elif objname == "acumulador_jornada":
			obj = AcumuladorJornada.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': AcumuladorJornada.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})
			
			
######## EDIT acumulador competicao #########
			
		elif objname == "acumulador_competicao":
			obj = AcumuladorCompeticao.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': AcumuladorCompeticao.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})
	
######## EDIT acumulador epoca #########
			
		elif objname == "acumulador_epoca":
			obj = AcumuladorEpoca.get_by_id(id)

			# now let's render the edit page
			self.render_subdir_to_output("admin", 'edit_%s.html' % objname, {
				'obj':obj, 'flash': flash_message,
				'objname': objname, 'fields': AcumuladorEpoca.fields, 'tab':tab,

				# editar this: editar fonte
				'edit': self.render_subdir("admin", 'obj_%s.html' % objname, {
						'edit':True, 'obj': obj
				})
			})