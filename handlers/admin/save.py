# -*- coding: utf-8 -*-
from google.appengine.api import memcache

import os
import datetime
import logging
import re
import config 
import urllib
from classes import *

from lib import mymemcache
from lib.myhandler import MyHandler

class Save(MyHandler):
	
	def post(self, objname):
		
		id = int(self.request.get('id'))
		new_sid = mymemcache.generate_sid()
	
		referer = urllib.unquote_plus(self.request.get('referrer'))   
		if not referer:
			referer = os.environ['HTTP_REFERER'] 
		flash_messages = []

		date = datetime.datetime.now()
		objs = []
		memcache_objs = {}
		
		if objname == "clube":
			obj = Clube.get_by_id(id)
			fields = Clube.fields
		elif objname == "jogador":
			obj = Jogador.get_by_id(id)
			fields = Jogador.fields
		elif objname == "epoca":
			obj = Epoca.get_by_id(id)
			fields = Epoca.fields
		elif objname == "competicao":
			obj = Competicao.get_by_id(id)
			fields = Competicao.fields
		elif objname == "jogo":
			obj = Jogo.get_by_id(id)
			fields = Jogo.fields
		elif objname == "arbitro":
			obj = Arbitro.get_by_id(id)
			fields = Arbitro.fields
		elif objname == "comentador":
			obj = Comentador.get_by_id(id)
			fields = Comentador.fields
		elif objname == "fonte":
			obj = Fonte.get_by_id(id)
			fields = Fonte.fields
		elif objname == "jornada":
			obj = Jornada.get_by_id(id)
			fields = Jornada.fields
		elif objname == "lance":
			obj = Lance.get_by_id(id)
			fields = Lance.fields
			
		elif objname == "clube_tem_jogador":
			obj = ClubeTemJogador.get_by_id(id)
			fields = ClubeTemJogador.fields
		elif objname == "clube_joga_competicao":
			obj = ClubeJogaCompeticao.get_by_id(id)
			fields = ClubeJogaCompeticao.fields
		elif objname == "jogador_joga_jogo":
			obj = JogadorJogaJogo.get_by_id(id)
			fields = JogadorJogaJogo.fields
		elif objname == "comentador_comenta_lance":
			obj = ComentadorComentaLance.get_by_id(id)
			fields = ComentadorComentaLance.fields
		elif objname == "jogador_em_lance":
			obj = JogadorEmLance.get_by_id(id)
			fields = JogadorEmLance.fields

		elif objname == "acumulador_jornada":
			obj = AcumuladorJornada.get_by_id(id)
			fields = AcumuladorJornada.fields
		elif objname == "acumulador_competicao":
			obj = AcumuladorCompeticao.get_by_id(id)
			fields = AcumuladorCompeticao.fields
		elif objname == "acumulador_epoca":
			obj = AcumuladorEpoca.get_by_id(id)
			fields = AcumuladorEpoca.fields

#############
### EPOCA ###
#############

		if objname == "epoca": 
			
			# obrigatórios
			obj.epo_ultima_alteracao = date
			obj.epo_nome = self.request.get('epo_nome')
			obj.epo_data_inicio = datetime.datetime.strptime(
				self.request.get('epo_data_inicio'), "%Y-%m-%d").date() 
			obj.epo_data_fim = datetime.datetime.strptime(
				self.request.get('epo_data_fim'), "%Y-%m-%d").date()
					
			objs.append(obj)
			memcache_objs[str(id)] = obj
			
##################
### COMPETICAO ###
##################

		elif objname == "competicao": 
			
			epoca = None
			try:
				epoca = Epoca.get_by_id(int(self.request.get('cmp_epoca_id')))
			except:
				error = u"Erro: Não encontrei época %s!" % self.request.get('cmp_epoca_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			lugares_descida = []
			empty = True
			if self.request.get_all('cmp_lugares_descida'):
				for item in self.request.get_all('cmp_lugares_descida'):
					if item != "": 
						empty = False
						
			if not empty:
				for item in self.request.get_all('cmp_lugares_descida'):
					if item != "":
						lugares_descida.append(int(item))

			lugares_liga_campeoes = []
			empty = True
			if self.request.get_all('cmp_lugares_liga_campeoes'):
				for item in self.request.get_all('cmp_lugares_liga_campeoes'):
					if item != "": 
						empty = False
						
			if not empty:
				for item in self.request.get_all('cmp_lugares_liga_campeoes'):
					if item != "":
						lugares_liga_campeoes.append(int(item))

			lugares_liga_europa = []
			empty = True
			if self.request.get_all('cmp_lugares_liga_europa'):
				for item in self.request.get_all('cmp_lugares_liga_europa'):
					if item != "": 
						empty = False
						
			if not empty:
				for item in self.request.get_all('cmp_lugares_liga_europa'):
					if item != "":
						lugares_liga_europa.append(int(item))

			lugares_eliminatorias_liga_campeoes = []
			empty = True
			if self.request.get_all('cmp_lugares_eliminatorias_liga_campeoes'):
				for item in self.request.get_all('cmp_lugares_eliminatorias_liga_campeoes'):
					if item != "": 
						empty = False
						
			if not empty:
				for item in self.request.get_all('cmp_lugares_eliminatorias_liga_campeoes'):
					if item != "":
						lugares_eliminatorias_liga_campeoes.append(int(item))

			obj.cmp_ultima_alteracao = date
			obj.cmp_nome = epoca.epo_nome+":"+self.request.get('cmp_tipo')
			obj.cmp_nome_completo = self.request.get('cmp_nome_completo')
			obj.cmp_numero_jornadas = int(self.request.get('cmp_numero_jornadas'))
			obj.cmp_tipo = self.request.get('cmp_tipo')
			obj.cmp_link_foto = self.request.get('cmp_link_foto')
			obj.cmp_link_zz = db.Link(self.request.get('cmp_link_zz'))
			obj.cmp_epoca = epoca
			obj.cmp_lugares_descida = lugares_descida
			obj.cmp_lugares_liga_campeoes = lugares_liga_campeoes
			obj.cmp_lugares_liga_europa = lugares_liga_europa
			obj.cmp_lugares_eliminatorias_liga_campeoes = lugares_eliminatorias_liga_campeoes
			
			epoca.epo_ultima_alteracao = date
			objs.append(obj)
			objs.append(epoca)
			memcache_objs[str(id)] = obj
			memcache_objs[str(epoca.key().id())] = epoca

###############
### JORNADA ###
###############

		elif objname == "jornada":
			
			competicao = None
			try:
				competicao = Competicao.get_by_id(int(self.request.get('jor_competicao_id')))
			except: 
				error = u"Erro: Não encontrei competição com id %s!" % self.request.get('jor_competicao_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			data = datetime.datetime.strptime(
				self.request.get('jor_data'), "%Y-%m-%d") if \
					self.request.get('jor_data') else None

			obj.jor_ultima_alteracao = date
			obj.jor_nome = competicao.cmp_nome+":"+self.request.get('jor_nome_curto')	
			obj.jor_data = data.date() if data else None	
			obj.jor_epoca = competicao.cmp_epoca
			obj.jor_competicao = competicao
			obj.jor_nome_curto = self.request.get('jor_nome_curto')
			obj.jor_nome_completo = self.request.get('jor_nome_completo')
			obj.jor_ordem = int(self.request.get('jor_ordem'))
			obj.jor_link_zz = db.Link(self.request.get('jor_link_zz'))

			competicao.cmp_epoca.epo_ultima_alteracao = date
			competicao.cmp_ultima_alteracao = date
			objs.append(obj)
			objs.append(competicao)
			objs.append(competicao.cmp_epoca)
			memcache_objs[str(id)] = obj
			memcache_objs[str(competicao.key().id())] = competicao
			memcache_objs[str(competicao.cmp_epoca.key().id())] = competicao.cmp_epoca

############
### JOGO ###
############

		elif objname == "jogo":
			
			jornada = Jornada.all().filter("jor_nome = ", self.request.get('jog_jornada')).get()
			clube_casa = None
			clube_fora = None
			
			if not jornada:
				error = u"Erro: Não encontrei jornada %s!" % self.request.get('jog_jornada')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
				
			try:
				clube_casa = Clube.get_by_id(int(self.request.get('jog_clube1_id')))
			except:
				error = u"Erro: Não encontrei clube de casa com nome %s!" % \
				 self.request.get('jog_clube1_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
				
			try:
				clube_fora = Clube.get_by_id(int(self.request.get('jog_clube2_id')))
			except:
				error = u"Erro: Não encontrei clube visitante com nome %s!" % self.request.get('jog_clube2_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			arbitro = None
			# arbitro pode vir já com id, por exemplo na página edit de um árbitro pode-ser criar um jogo
			try:
				arbitro = Arbitro.get_by_id(int(self.request.get('jog_arbitro_id')))
			except:
				pass

			list_link_sites = []
			empty = True
			if self.request.get_all('jog_link_sites'):
				for item in self.request.get_all('jog_link_sites'):
					if item != u"": 
						empty = False
			
			if not empty:
				for link_site in self.request.get_all('jog_link_sites'):
					if link_site != "":
						list_link_sites.append(db.Link(link_site))
			
			#logging.info(list_link_sites)
			list_link_videos = []
			
			empty = True
			if self.request.get_all('jog_link_videos'):
				for item in self.request.get_all('jog_link_videos'):
					if item != u"": 
						empty = False

			if not empty:
				for link_video in self.request.get_all('jog_link_videos'):
					if link_video != "":
						list_link_videos.append(db.Text(link_video))

			data = None
			try:
				data = datetime.datetime.strptime(self.request.get('jog_data'), "%Y-%m-%d %H:%M") 
			except:
				data = None
					
			clubes = []
			if clube_casa:
				clubes.append(clube_casa.key())
                        if clube_fora:
                                clubes.append(clube_fora.key())

			obj.jog_ultima_alteracao = date
			obj.jog_nome = jornada.jor_nome+":"+clube_casa.clu_nome+":"+clube_fora.clu_nome
			obj.jog_epoca = jornada.jor_competicao.cmp_epoca
			obj.jog_competicao = jornada.jor_competicao
			obj.jog_jornada = jornada
			obj.jog_data = data
			obj.jog_clube1 = clube_casa
			obj.jog_clube2 = clube_fora
			obj.jog_clubes = clubes
			obj.jog_tactica_clube1 = self.request.get('jog_tactica_clube1')
			obj.jog_tactica_clube2 = self.request.get('jog_tactica_clube2')
			obj.jog_arbitro = arbitro if arbitro else None
			obj.jog_golos_clube1 = int(self.request.get('jog_golos_clube1')) if \
				self.request.get('jog_golos_clube1') else None
			obj.jog_golos_clube2 = int(self.request.get('jog_golos_clube2')) if \
				self.request.get('jog_golos_clube2') else None
			obj.jog_link_sites = list_link_sites
			obj.jog_link_videos = list_link_videos
			obj.jog_comentario = self.request.get('jog_comentario')
			
			clube_casa.clu_ultima_alteracao = date
			clube_fora.clu_ultima_alteracao = date
			jornada.jor_competicao.cmp_epoca.epo_ultima_alteracao = date
			jornada.jor_competicao.cmp_ultima_alteracao = date
			objs.append(obj)
			objs.append(clube_casa)
			objs.append(clube_fora)
			objs.append(jornada.jor_competicao)
			objs.append(jornada.jor_competicao.cmp_epoca)
			memcache_objs = {str(id): obj, 
				str(clube_casa.key().id()): clube_casa,
				str(clube_fora.key().id()): clube_fora,
				str(jornada.jor_competicao.key().id()): jornada.jor_competicao,
				str(jornada.jor_competicao.cmp_epoca.key().id()): jornada.jor_competicao.cmp_epoca
			}
			if arbitro:
				arbitro.arb_ultima_alteracao = date
				objs.append(arbitro)
				memcache_objs[str(arbitro.key().id())] = arbitro

#############
### LANCE ###
#############

		elif objname == "lance":
			
			jogo = Jogo.all().filter("jog_nome = ", self.request.get('lan_jogo')).get()
					
			if not jogo: 
				error = u"Erro: Não encontrei jogo com id %s!" % self.request.get('lan_jogo')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			list_link_sites = []
			empty = True
			if self.request.get_all('lan_link_sites'):
				for item in self.request.get_all('lan_link_sites'):
					if item != u"": 
						empty = False

			if not empty:
				for link_site in self.request.get_all('lan_link_sites'):
					if link_site != "":
						list_link_sites.append(db.Link(link_site))
			
			list_link_videos = []
			empty = True
			if self.request.get_all('lan_link_videos'):
				for item in self.request.get_all('lan_link_videos'):
					if item != u"": 
						empty = False
			
			if not empty:
				for link_video in self.request.get_all('lan_link_videos'):
					if link_video != "":
						list_link_videos.append(db.Text(link_video))
			
			minuto = 0
			if self.request.get('lan_minuto'):
				minuto = int(self.request.get('lan_minuto'))

			obj.lan_ultima_alteracao = date
			obj.lan_nome = jogo.jog_nome+":"+self.request.get('lan_numero')
			obj.lan_epoca = jogo.jog_jornada.jor_competicao.cmp_epoca
			obj.lan_competicao = jogo.jog_jornada.jor_competicao
			obj.lan_jornada = jogo.jog_jornada
			obj.lan_jogo = jogo
			obj.lan_data = jogo.jog_data
			obj.lan_arbitro = jogo.jog_arbitro 
			obj.lan_clube1 = jogo.jog_clube1
			obj.lan_clube2 = jogo.jog_clube2
			obj.lan_numero = int(self.request.get('lan_numero'))
			obj.lan_minuto = minuto
			obj.lan_descricao = self.request.get('lan_descricao')
			obj.lan_classe =  int(self.request.get('lan_classe'))
			obj.lan_link_sites = list_link_sites
			obj.lan_link_videos = list_link_videos
			obj.lan_comentario = self.request.get('lan_comentario')

			jogo.jog_clube1.clu_ultima_alteracao = date
			jogo.jog_clube2.clu_ultima_alteracao = date
			jogo.jog_jornada.jor_ultima_alteracao = date
			jogo.jog_jornada.jor_competicao.cmp_ultima_alteracao = date
			jogo.jog_jornada.jor_competicao.cmp_epoca.epo_ultima_alteracao = date
			objs.append(obj)
			objs.append(jogo)
			objs.append(jogo.jog_clube1)
			objs.append(jogo.jog_clube2)
			objs.append(jogo.jog_jornada)
			objs.append(jogo.jog_jornada.jor_competicao)
			objs.append(jogo.jog_jornada.jor_competicao.cmp_epoca)
			memcache_objs = {str(id): obj, 
				str(jogo.key().id()): jogo,				
				str(jogo.jog_clube1.key().id()): jogo.jog_clube1,
				str(jogo.jog_clube1.key().id()): jogo.jog_clube1,
				str(jogo.jog_jornada.key().id()): jogo.jog_jornada,
				str(jogo.jog_jornada.jor_competicao.key().id()): jogo.jog_jornada.jor_competicao,
				str(jogo.jog_jornada.jor_competicao.cmp_epoca.key().id()): jogo.jog_jornada.jor_competicao.cmp_epoca
			}
			if jogo.jog_arbitro:
				objs.append(jogo.jog_arbitro)
				memcache_objs[str(jogo.jog_arbitro.key().id())] = jogo.jog_arbitro

#############
### CLUBE ###
#############	
			
		elif objname == "clube":
			obj.clu_ultima_alteracao = date
			obj.clu_nome_completo = self.request.get('clu_nome_completo')
			obj.clu_nome_curto = self.request.get('clu_nome_curto')
			# é para deixar estar?
			obj.clu_nome = self.request.get('clu_nome')
			obj.clu_link_logo = self.request.get('clu_link_logo')
			obj.clu_link_zz = db.Link(self.request.get('clu_link_zz'))

			objs.append(obj)
			memcache_objs.update({str(id):obj})

###############
### JOGADOR ###
###############	

		elif objname == "jogador": 
			
			numero = None
			clube = None
			
			try:
				numero = int(self.request.get('jgd_numero'))
			except:
				numero = 0

			obj.jgd_ultima_alteracao = date
			obj.jgd_nome = self.request.get('jgd_nome')
			obj.jgd_nome_completo = self.request.get('jgd_nome_completo')
			obj.jgd_numero = numero
			obj.jgd_link_foto = self.request.get('jgd_link_foto')
			obj.jgd_link_zz = db.Link(self.request.get('jgd_link_zz'))
			
			posicao = []
			if self.request.get_all('jgd_posicao'):
				for pos in self.request.get_all('jgd_posicao'):
					if pos != "":
						posicao.append(pos)
			
			try:
				clube = Clube.get_by_id(int(self.request.get('jgd_clube_actual_id')))
			except: 
				error = u"Erro: Não encontrei clube com id %s!" % \
				 self.request.get('jgd_clube_actual_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
				
			obj.jgd_clube_actual = clube			
			obj.jgd_posicao = posicao

			clube.clu_ultima_alteracao = date
			objs.append(obj)
			objs.append(clube)
			memcache_objs[str(id)] = obj
			memcache_objs[str(clube.key().id())] = clube
			
###############
### ARBITRO ###
###############	

		elif objname == "arbitro":
			
			obj.arb_ultima_alteracao = date
			obj.arb_nome = self.request.get('arb_nome')
			obj.arb_link_foto = self.request.get('arb_link_foto')
			obj.arb_link_zz = db.Link(self.request.get('arb_link_zz'))

##################
### COMENTADOR ###
##################	
		
		elif objname == "comentador":
			
			fonte = Fonte.all().filter("fon_nome = ", self.request.get('com_fonte')).get()
			if not fonte: 
				error = u"Erro: Não encontrei fonte com nome %s!" % self.request.get('com_fonte')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return 
				
			obj.com_ultima_alteracao = date
			obj.com_nome = self.request.get('com_nome')
			obj.com_link_foto = self.request.get('com_link_foto')
			obj.com_link = self.request.get('com_link')
			obj.com_fonte = fonte

			fonte.fon_ultima_alteracao = date
			objs.append(obj)
			objs.append(fonte)
			memcache_objs[str(id)] = obj
			memcache_objs[str(fonte.key().id())] = fonte

#############
### FONTE ###
#############	
			
		elif objname == "fonte":
			
			obj.fon_ultima_alteracao = date
			obj.fon_nome = self.request.get('fon_nome')
			obj.fon_link = db.Link(self.request.get('fon_link'))

			objs.append(obj)
			memcache_objs[str(id)] = obj

#########################
### CLUBE_TEM_JOGADOR ###
#########################
			
		elif objname == "clube_tem_jogador": 
			
			clube = None
			try:
				clube = Clube.get_by_id(int(self.request.get('ctj_clube_id')))
			except:
				error = u"Erro: Não encontrei clube com nome %s!" % self.request.get('ctj_clube_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			jogador = Jogador.all().filter("jgd_nome= ", self.request.get('ctj_jogador')).get()
				
			if not jogador: 
				error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get('ctj_jogador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			epocas = []
			for epoca_id in self.request.get_all('ctj_epocas_id'):
				if epoca_id != "":
					epoca = None
					try:
						epoca = Epoca.get_by_id(int(epoca_id))
					except:
						pass
						#epoca = Epoca.all().filter("__key__ in", [db.Key(epoca_nome)]).get()
						
					if epoca:	
						epocas.append(epoca.key()) 
			
			obj.ctj_clube = clube
			obj.ctj_jogador = jogador
			obj.ctj_epocas = epocas
			obj.ctj_numero = int(self.request.get('ctj_numero')) if self.request.get('ctj_numero') else None

			clube.clu_ultima_alteracao = date
			jogador.jgd_ultima_alteracao = date
			objs.append(clube)
			objs.append(jogador)
			objs.append(obj)
			memcache_objs[str(clube.key().id())] = clube
			memcache_objs[str(jogador.key().id())] = jogador

#############################
### CLUBE_JOGA_COMPETICAO ###
#############################
			
		elif objname == "clube_joga_competicao": 
			
			clube = None
			competicao = None
			
			try:
				clube = Clube.get_by_id(int(self.request.get('cjc_clube_id')))
			except:
				error = u"Erro: Não encontrei clube com id %s!" % self.request.get('cjc_clube_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			try:
				competicao =  Competicao.get_by_id(int(self.request.get('cjc_competicao_id')))
			except: 
				error = u"Erro: Não encontrei competição com id %s!" % self.request.get('cjc_competicao_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			cjc_classificacao_anterior = 0
			try:
				cjc_classificacao_anterior = int(self.request.get('cjc_classificacao_anterior'))
			except:
				cjc_classificacao_anterior = 0
					
			# agora que está tudo sanitanizado, toca a inserir
			obj.cjc_clube = clube
			obj.cjc_competicao = competicao
			obj.cjc_classificacao_anterior = cjc_classificacao_anterior

			clube.clu_ultima_alteracao = date
			competicao.cmp_ultima_alteracao = date
			objs.append(clube)
			objs.append(competicao)
			objs.append(obj)
			memcache_objs[str(clube.key().id())] = clube
			memcache_objs[str(competicao.key().id())] = competicao

#########################
### JOGADOR_JOGA_JOGO ###
#########################
			
		elif objname == "jogador_joga_jogo": 
			
			clube = None
			jogador = Jogador.all().filter("jgd_nome= ", self.request.get('jjj_jogador')).get()
			if not jogador: 
				error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get('jjj_jogador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
				
			jogo =  Jogo.all().filter("jog_nome = ", self.request.get('jjj_jogo')).get()
		
			if not jogo: 
				error = u"Erro: Não encontrei jogo com id %s!" % self.request.get('jog_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
#				self.redirect('/%(objname)s/edit?id=%(id)s' % {'objname' : objname, 'id' : id})
				return
			
			try:
				clube= Clube.get_by_id(int(self.request.get('jjj_clube_id')))
			except: 
				error = u"Erro: Não encontrei jogador com id %s!" % self.request.get('jjj_clube_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			# tem de ser assim!
			amarelo = None
			if self.request.get('jjj_amarelo_minuto'):
				amarelo = int(self.request.get('jjj_amarelo_minuto'))
			duplo_amarelo = None
			if self.request.get('jjj_duplo_amarelo_minuto'):
				duplo_amarelo = int(self.request.get('jjj_duplo_amarelo_minuto'))
			vermelho = None
			if self.request.get('jjj_vermelho_minuto'):
				vermelho = int(self.request.get('jjj_vermelho_minuto'))
			substituicao_entrada = None
			if self.request.get('jjj_substituicao_entrada'):
				substituicao_entrada = int(self.request.get('jjj_substituicao_entrada'))
			substituicao_saida = None
			if self.request.get('jjj_substituicao_saida'):
				substituicao_saida = int(self.request.get('jjj_substituicao_saida'))
			
			obj.jjj_jogador = jogador
			obj.jjj_jogo = jogo
			obj.jjj_clube = clube
			obj.jjj_amarelo_minuto = amarelo
			obj.jjj_duplo_amarelo_minuto = duplo_amarelo
			obj.jjj_vermelho_minuto = vermelho
			obj.jjj_substituicao_entrada =substituicao_entrada
			obj.jjj_substituicao_saida = substituicao_saida
			obj.jjj_posicao = self.request.get('jjj_posicao')

			list = [] 
			list_tipos = []
			list_tipos_x = self.request.get_all('jjj_golos_tipos')

			empty = True
			if self.request.get_all('jjj_golos_minutos'):
				for item in self.request.get_all('jjj_golos_minutos'):
					if item != u"": 
						empty = False

			if empty:
				obj.jjj_golos_minutos = list
			else:
				for idx, minuto in enumerate(self.request.get_all('jjj_golos_minutos')):
					if minuto != "": 
						list.append(int(minuto))
						if len(list_tipos_x) > idx:
							list_tipos.append( list_tipos_x[idx] )
						else:
							list_tipos.append('')
				if list:
					obj.jjj_golos_minutos = list
					obj.jjj_golos_tipos = list_tipos
		

			list_link_videos = []
			for link_video in self.request.get_all('jjj_golos_link_videos'):
				if link_video != "":
					list_link_videos.append(db.Text(link_video))
				
			if list_link_videos:
				obj.jjj_golos_link_videos = list_link_videos

			jogo.jog_ultima_alteracao = date
			jogador.jgd_ultima_alteracao = date
			clube.clu_ultima_alteracao = date
			objs.append(jogo)
			objs.append(jogador)
			objs.append(clube)
			objs.append(obj)
			memcache_objs[str(jogo.key().id())] = jogo
			memcache_objs[str(jogador.key().id())] = jogador
			memcache_objs[str(clube.key().id())] = clube
	
################################
### COMENTADOR_COMENTA_LANCE ###
################################

		elif objname == "comentador_comenta_lance": 
			
			comentador = None
			try:
				comentador = Comentador.get_by_id(int(self.request.get('ccl_comentador_id')))
			except:
				error = u"Erro: Não encontrei comentador com nome %s!" % self.request.get('ccl_comentador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
				
			lance =  Lance.all().filter("lan_nome = ", self.request.get('ccl_lance')).get()

			if not lance: 
				error = u"Erro: Não encontrei lance %s!" % self.request.get('ccl_lance')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
				
			# agora que está tudo sanitanizado, toca a inserir
			obj.ccl_comentador = comentador
			obj.ccl_lance = lance
			obj.ccl_descricao = self.request.get('ccl_descricao')
			obj.ccl_decisao = int(self.request.get('ccl_decisao'))

			comentador.com_ultima_alteracao = date
			lance.lan_ultima_alteracao = date
			lance.lan_jogo.jog_ultima_alteracao = date
			lance.lan_clube1.clu_ultima_alteracao = date
			lance.lan_clube2.clu_ultima_alteracao = date
			lance.lan_jornada.jor_ultima_alteracao = date
			lance.lan_epoca.epo_ultima_alteracao = date
			lance.lan_competicao.cmp_ultima_alteracao = date

			objs.append(comentador)
			objs.append(lance)
			objs.append(lance.lan_jogo)
			objs.append(lance.lan_clube1)
			objs.append(lance.lan_clube2)
			objs.append(lance.lan_jornada)
			objs.append(lance.lan_competicao)
			objs.append(lance.lan_epoca)
			objs.append(obj)
			
			memcache_objs = {str(id): obj, 
				str(comentador.key().id()): comentador,
				str(lance.key().id()): lance,
				str(lance.lan_jogo.key().id()): lance.lan_jogo,
				str(lance.lan_clube1.key().id()): lance.lan_clube1,
				str(lance.lan_clube2.key().id()): lance.lan_clube2,
				str(lance.lan_jornada.key().id()): lance.lan_jornada,
				str(lance.lan_competicao.key().id()): lance.lan_competicao,
				str(lance.lan_epoca.key().id()): lance.lan_epoca
			}
			if lance.lan_arbitro:
				objs.append(lance.lan_arbitro)
				memcache_objs[str(lance.lan_arbitro.key().id())] = lance.lan_arbitro

########################
### JOGADOR_EM_LANCE ###
########################
			
		elif objname == "jogador_em_lance": 
			
			jogador = Jogador.all().filter("jgd_nome= ", self.request.get('jel_jogador')).get()
			if not jogador: 
				error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get('jel_jogador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			lance =  Lance.all().filter("lan_nome = ", self.request.get('jel_lance')).get()
				
			if not lance: 
				error = u"Erro: Não encontrei lance %s!" % self.request.get('jel_lance')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))
				return
			
			# agora que está tudo sanitanizado, toca a inserir
			obj.jel_jogador = jogador
			obj.jel_lance = lance
			obj.jel_papel = self.request.get('jel_papel')

			jogador.jgd_ultima_alteracao = date
			lance.lan_ultima_alteracao = date
			lance.lan_jogo.jog_ultima_alteracao = date
			objs.append(lance.lan_jogo)
			objs.append(jogador)
			objs.append(lance)
			objs.append(obj)
			memcache_objs[str(lance.lan_jogo.key().id())] = lance.lan_jogo
			memcache_objs[str(jogador.key().id())] = jogador
			memcache_objs[str(lance.key().id())] = lance

# put object	

		db.put(objs)
		memcache.set_multi(memcache_objs, time=86400)
		
		flash_messages.append(u"%s %s editada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
		memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
		return self.redirect(mymemcache.add_sid_to_cookie(referer, new_sid))

