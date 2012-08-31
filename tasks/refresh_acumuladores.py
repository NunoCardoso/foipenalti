# -*- coding: utf-8 -*-

from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import re
import traceback
import datetime

from classes import *
from lib import acumulador_jornada
from lib import acumulador_competicao
from lib import acumulador_epoca
from lib.myhandler import MyHandler
import lib.mymemcache

class Refresh(MyHandler):
	
	def get(self, action):
	
		date = datetime.datetime.now()
		flash_messages=[]


		if action == "1j1c1e":
		
##############
### 1J1C1E ###
##############
			versao = None
			try:
				versao = int(self.request.get('versao'))
			except:
				versao = config.VERSAO_ACUMULADOR
		
# JORNADA
			
			jornada = None
			try:
				jornada = Jornada.all().filter("jor_nome = ", self.request.get("jornada")).get()
			except:
				error = u"Erro: Não encontrei jornada %s!" % self.request.get('jornada')
				logging.error(error)
				return
				
			stats_jornada = acumulador_jornada.gera(jornada)
			
			obj = AcumuladorJornada.all().filter("acuj_jornada = ", jornada).filter("acuj_versao = ", versao).get()
			if not obj:
				obj = AcumuladorJornada(
					acuj_epoca = jornada.jor_competicao.cmp_epoca,
					acuj_competicao = jornada.jor_competicao,
					acuj_jornada = jornada
				)
				
			obj.acuj_date = date
			obj.acuj_versao = versao
			obj.acuj_content = stats_jornada
			obj.put()
			
			# os acumuladores não são chamados por ID, mas por namespaces/jor-cmp-epo 
			memcache.set(u"acumulador-%s-%s" % (jornada, versao), obj, time=86400)
			message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj) 
			flash_messages.append(message)
			logging.info(message)
			
#COMPETICAO
			
		#	stats = acumulador_competicao.gera(competicao, acuc_basico, 
		#		acuc_classificacao, acuc_tabela_icc, acuc_icc, acuc_top_arbitros,
		#		acuc_top_jogos, acuc_top_jogadores, acuc_top_clubes)
			stats = acumulador_competicao.gera(jornada.jor_competicao, "on", 
				"on", "on", "on", "on", "on", "on", "on")
		
			for namespace in AcumuladorCompeticao.acuc_namespaces:
				obj = AcumuladorCompeticao.all().filter("acuc_competicao = ",
				 jornada.jor_competicao).filter("acuc_versao =", versao).filter(
					"acuc_namespace =", namespace).get()
				if not obj:
					obj = AcumuladorCompeticao(
					acuc_competicao = jornada.jor_competicao,
					acuc_epoca = jornada.jor_competicao.cmp_epoca
					)
					
				obj.acuc_namespace = namespace
				obj.acuc_versao = versao
				obj.acuc_date = date
				obj.acuc_content = {namespace : stats[namespace]}
				
				obj.put()
				memcache.set(u"acumulador-%s-%s" % (jornada.jor_competicao, str(versao)), 
					obj, namespace=namespace, time=86400)
				message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj) 
				flash_messages.append(message)
				logging.info(message)
				
# EPOCA
			# stats = acumulador_epoca.gera(epoca, acue_basico, 
			# 	acue_tabela_icc, acue_icc, acue_top_arbitros,
			# 	acue_top_jogos, acue_top_jogadores, acue_top_clubes)
			stats = acumulador_epoca.gera(jornada.jor_competicao.cmp_epoca, 
			"on","on","on","on","on","on","on") 

			for namespace in AcumuladorEpoca.acue_namespaces:
				obj = AcumuladorEpoca.all().filter("acue_epoca = ",
				 jornada.jor_competicao.cmp_epoca).filter("acue_versao =", versao).filter(
					"acue_namespace =", namespace).get()
				if not obj:
					obj = AcumuladorEpoca(
					acue_epoca = jornada.jor_competicao.cmp_epoca
					)
					
				
				obj.acue_namespace = namespace
				obj.acue_versao = versao
				obj.acue_date = date
				obj.acue_content = {namespace : stats[namespace]}
				
				obj.put()
				memcache.set(u"acumulador-%s-%s" % (jornada.jor_competicao.cmp_epoca, str(versao)), 
					obj, namespace=namespace, time=86400)
				message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj ) 
				flash_messages.append(message)
				logging.info(message)

			return self.response.out.write("<BR>".join(flash_messages))



		elif action == "1j":
		
##########
### 1J ###
##########
			versao = None
			try:
				versao = int(self.request.get('versao'))
			except:
				versao = config.VERSAO_ACUMULADOR
		
# JORNADA
			
			jornada = None
			try:
				jornada = Jornada.all().filter("jor_nome = ", self.request.get("jornada")).get()
			except:
				error = u"Erro: Não encontrei jornada %s!" % self.request.get('jornada')
				logging.error(error)
				return
				
			stats_jornada = acumulador_jornada.gera(jornada)
			
			obj = AcumuladorJornada.all().filter("acuj_jornada = ", jornada).filter("acuj_versao = ", versao).get()
			if not obj:
				obj = AcumuladorJornada(
					acuj_epoca = jornada.jor_competicao.cmp_epoca,
					acuj_competicao = jornada.jor_competicao,
					acuj_jornada = jornada
				)
				
			obj.acuj_date = date
			obj.acuj_versao = versao
			obj.acuj_content = stats_jornada
			obj.put()
			
			# os acumuladores não são chamados por ID, mas por namespaces/jor-cmp-epo 
			memcache.set(u"acumulador-%s-%s" % (jornada, versao), obj, time=86400)
			message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj) 
			flash_messages.append(message)
			logging.info(message)
			return self.response.out.write("<BR>".join(flash_messages))

##########
### 1E ###
##########

		elif action == "1e":

			versao = None
			try:
				versao = int(self.request.get('versao'))
			except:
				versao = config.VERSAO_ACUMULADOR
			
			epoca = None
			try:
				epoca = Epoca.all().filter("epo_nome = ", self.request.get("epoca")).get()
			except:
				error = u"Erro: Não encontrei época %s!" % self.request.get('epoca')
				logging.error(error)
				return
				
			for competicao in epoca.epo_competicoes:
				for jornada in competicao.cmp_jornadas.order("jor_ordem"):
					stats_jornada = acumulador_jornada.gera(jornada)
			
					obj = AcumuladorJornada.all().filter("acuj_jornada = ", jornada).filter("acuj_versao = ", versao).get()
			
					if not obj:
						obj = AcumuladorJornada(
							acuj_epoca = jornada.jor_competicao.cmp_epoca,
							acuj_competicao = jornada.jor_competicao,
							acuj_jornada = jornada
						)
						
					obj.acuj_versao = versao
					obj.acuj_date = date
					obj.acuj_content = stats_jornada
					obj.put()
			
					# os acumuladores não são chamados por ID, mas por namespaces/jor-cmp-epo 
					memcache.set(u"acumulador-%s-%s" % (jornada, str(versao)), obj, time=86400)
					message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj) 
					flash_messages.append(message)
					logging.info(message)
			
				stats = acumulador_competicao.gera(jornada.jor_competicao, "on", 
				"on", "on", "on", "on", "on", "on", "on")
		
				for namespace in AcumuladorCompeticao.acuc_namespaces:
					obj = AcumuladorCompeticao.all().filter("acuc_competicao = ",
					competicao).filter("acuc_versao =", versao).filter(
					"acuc_namespace =", namespace).get()
					if not obj:
						obj = AcumuladorCompeticao(
							acuc_epoca = competicao.cmp_epoca,
							acuc_competicao = competicao
						)
						
					obj.acuc_namespace = namespace
					obj.acuc_versao = versao
					obj.acuc_date = date
					obj.acuc_content = {namespace : stats[namespace]}
					
					obj.put()
					memcache.set(u"acumulador-%s-%s" % (competicao, str(versao)), 
						obj, namespace=namespace, time=86400)
					message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj) 
					flash_messages.append(message)
					logging.info(message)
			
			stats = acumulador_epoca.gera(jornada.jor_competicao.cmp_epoca, 
			"on","on","on","on","on","on","on") 

			for namespace in AcumuladorEpoca.acue_namespaces:
				obj = AcumuladorEpoca.all().filter("acue_epoca = ",
				 jornada.jor_competicao.cmp_epoca).filter("acue_versao =", versao).filter(
					"acue_namespace =", namespace).get()
				if not obj:
					obj = AcumuladorEpoca(
						acue_epoca = jornada.jor_competicao.cmp_epoca
					)
					
				obj.acue_namespace = namespace
				obj.acue_versao = versao
				obj.acue_date = date
				obj.acue_content = {namespace : stats[namespace]}
				
				obj.put()
				memcache.set(u"acumulador-%s-%s" % (epoca, str(versao)), 
					obj, namespace=namespace, time=86400)
				message = u"Refresh task %s: %s %s adicionada." % (action, obj.kind(), obj) 
				flash_messages.append(message)
				logging.info(message)
