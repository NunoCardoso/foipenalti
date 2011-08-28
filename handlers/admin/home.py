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
from list import List
from lib import listas
## recebe pedidos, faz splash screens

class RedirectHome(MyHandler):
		
	def get(self, objname):
		
		# enforce a trailing slash
		return self.redirect(self.request.url+"/")

class Home(MyHandler):
		
	def get(self, objname):
		
		sid = self.request.get('sid')
		if sid:
			flash_message = memcache.get(str(sid), namespace="flash")
			if flash_message:
				memcache.delete(sid, namespace="flash")

		# gera a lista de entradas para este obj_name
		# objs, objname, filter_field, filter_needle, url, page_index, limit
		
		initial_objs = None
		fields = None
		
		tab = self.request.get("tab")
		
		if objname == "clube":
			initial_objs =  Clube.all()
			fields = Clube.fields
		elif objname == "jogador":
			initial_objs =  Jogador.all()
			fields = Jogador.fields
		elif objname == "epoca":
			initial_objs =  Epoca.all()
			fields = Epoca.fields
		elif objname == "competicao":
			initial_objs =  Competicao.all()
			fields = Competicao.fields
		elif objname == "jogo":
			initial_objs =  Jogo.all()
			fields = Jogo.fields
		elif objname == "arbitro":
			initial_objs =  Arbitro.all()
			fields = Arbitro.fields
		elif objname == "comentador":
			initial_objs =  Comentador.all()
			fields = Comentador.fields
		elif objname == "fonte":
			initial_objs =  Fonte.all()
			fields = Fonte.fields
		elif objname == "jornada":
			initial_objs =  Jornada.all()
			fields = Jornada.fields
		elif objname == "lance":
			initial_objs =  Lance.all()
			fields = Lance.fields
			
		elif objname == "clube_tem_jogador":
			initial_objs =  ClubeTemJogador.all()
			fields = ClubeTemJogador.fields
		elif objname == "clube_joga_competicao":
			initial_objs =  ClubeJogaCompeticao.all()
			fields = ClubeJogaCompeticao.fields
		elif objname == "jogador_joga_jogo":
			initial_objs =  JogadorJogaJogo.all()
			fields = JogadorJogaJogo.fields
		elif objname == "comentador_comenta_lance":
			initial_objs =  ComentadorComentaLance.all()
			fields = ComentadorComentaLance.fields
		elif objname == "jogador_em_lance":
			initial_objs =  JogadorEmLance.all()
			fields = JogadorEmLance.fields

		elif objname == "acumulador_jornada":
			initial_objs =  AcumuladorJornada.all()
			fields = AcumuladorJornada.fields
		elif objname == "acumulador_competicao":
			initial_objs =  AcumuladorCompeticao.all()
			fields = AcumuladorCompeticao.fields
		elif objname == "acumulador_epoca":
			initial_objs =  AcumuladorEpoca.all()
			fields = AcumuladorEpoca.fields
	
		lista = List().gera_lista({
			"objs":initial_objs, 
			"objname":objname, 
			"filter_field":None,
			"filter_needle":None, 
			"url":self.request.url, 
			"referrer":objname,
			"page_index":1, 
			"limit":15,
			"flash":None})

#############
### EPOCA ###
#############

		if objname == "epoca":
			
			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})

##################
### COMPETICAO ###
##################

		elif objname == "competicao":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True, 
				'epocas':listas.get_lista_epocas()
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10, 
				'epocas':listas.get_lista_epocas()
			})
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
				'new_multiple':new_multiple,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})

###############
### JORNADA ###
###############

		elif objname == "jornada":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True,
				'competicoes':listas.get_lista_competicoes()

			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10,
				'competicoes':listas.get_lista_competicoes()
			})
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
				'new_multiple':new_multiple,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})
			
############
### JOGO ###
############

		elif objname == "jogo":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True,
				'clubes':listas.get_lista_clubes(),# para select com clubes,
				'arbitros':listas.get_lista_arbitros(), # para select com árbitros,
				'tacticas':listas.get_lista_tacticas()
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10,
				'clubes':listas.get_lista_clubes(),# para select com clubes,
				'arbitros':listas.get_lista_arbitros(), # para select com árbitros,
				'tacticas':listas.get_lista_tacticas()
			})
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
				'new_multiple':new_multiple,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})

#############
### LANCE ###
#############

		elif objname == "lance":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True,
				'tipos_lances':listas.get_lista_tipos_lances(),
				'tipos_jels':listas.get_lista_tipos_jels(),
				'comentadores':listas.get_lista_comentadores()
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10,
				'tipos_lances':listas.get_lista_tipos_lances(),
				'tipos_jels':listas.get_lista_tipos_jels(),
				'comentadores':listas.get_lista_comentadores()
			})
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
				'new_multiple':new_multiple,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})

#############
### CLUBE ###
#############

		elif objname == "clube":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			# new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
			# 	'objname': objname,
			# 	'fields': fields,
			# 	'new_multiple':True,
			# 	'howmany':10
			# })
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
#				'new_multiple':new_multiple,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})

###############
### JOGADOR ###
###############

		elif objname == "jogador":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True,
				'posicoes': listas.get_lista_posicoes(),
				'clubes': listas.get_lista_clubes(),
				'epocas':listas.get_lista_epocas()
			})
		
			# new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
			# 	'objname': objname,
			# 	'fields': fields,
			# 	'new_multiple':True,
			# 	'howmany':10,
			# 	'posicoes': listas.get_lista_posicoes(),
			# 	'clubes': listas.get_lista_clubes(),
			#	'epocas':listas.get_lista_epocas()
			# })
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
				'new_single':new_single,
#				'new_multiple':new_multiple,
				'objname': objname,
				'flash': flash_message,
				'list': lista,
				'tab':tab
			})

###############
### ARBITRO ###
###############

		elif objname == "arbitro":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
			
			# new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
			# 	'objname': objname,
			# 	'fields': fields,
			# 	'new_multiple':True,
			# 	'howmany':10
			# })
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})

##################
### COMENTADOR ###
##################

		elif objname == "comentador":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})
			
#############
### FONTE ###
#############

		elif objname == "fonte":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})
			
#########################
### CLUBE_TEM_JOGADOR ###
#########################

		elif objname == "clube_tem_jogador":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10
			})	
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'new_multiple':new_multiple,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})			

#############################
### CLUBE_JOGA_COMPETICAO ###
#############################

		elif objname == "clube_joga_competicao":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10
			})	
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'new_multiple':new_multiple,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})			

#########################
### JOGADOR_JOGA_JOGO ###
#########################

		elif objname == "jogador_joga_jogo":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10
			})	
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'new_multiple':new_multiple,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})			

################################
### COMENTADOR_COMENTA_LANCE ###
################################

		elif objname == "comentador_comenta_lance":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10
			})	
						
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'new_multiple':new_multiple,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})			

########################
### JOGADOR_EM_LANCE ###
########################

		elif objname == "jogador_em_lance":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10
			})	
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'new_multiple':new_multiple,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})			


##########################
### ACUMULADOR JORNADA ###
##########################

		elif objname == "acumulador_jornada":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})

			new_multiple = self.render_subdir("admin", 'obj_%s_multiple.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_multiple':True,
				'howmany':10
			})
		
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'new_multiple':new_multiple,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})

##########################
### ACUMULADOR COMPETICAO ###
##########################

		elif objname == "acumulador_competicao":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})
			
##########################
### ACUMULADOR EPOCA ###
##########################

		elif objname == "acumulador_epoca":

			## TAB renders
			new_single = self.render_subdir("admin", 'obj_%s.html' % objname, {
				'objname': objname,
				'fields': fields,
				'new_single':True
			})
		
			
			## HOME render
			self.render_subdir_to_output("admin", 'home_'+objname+'.html', {
			'new_single':new_single,
			'objname': objname,
			'flash': flash_message,
			'list': lista,
			'tab':tab
			})
			