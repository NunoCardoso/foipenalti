# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

# .__str__().decode("utf-8","xmlcharrefreplace")

import os
import datetime
import logging
import re
import config 
import sys

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler
from lib import acumulador_jornada
from lib import acumulador_competicao
from lib import acumulador_epoca

class New(MyHandler):
	
	def post(self, objname):

		referer = os.environ['HTTP_REFERER'] 
			
		flash_messages = []
		date = datetime.datetime.now()
		new_sid = self.generate_sid()

#########
# EPOCA #
#########	
			
		if objname == "epoca": 
	
			obj = Epoca(
				epo_numero_visitas = 0,
				epo_ultima_alteracao = date,
				epo_nome = self.request.get('epo_nome'),
				epo_data_inicio = datetime.datetime.strptime(
					self.request.get('epo_data_inicio'), "%Y-%m-%d").date(),
				epo_data_fim = datetime.datetime.strptime(
					self.request.get('epo_data_fim'), "%Y-%m-%d").date()
			)
			
			obj.put()
			memcache.set_multi(
				{str(obj.key().id()):obj}, 
			time=86400)
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
				
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)

##############
# COMPETICAO #
##############

		elif objname == "competicao": 
			
			# pode ser que venha uma epo_id de, por exemplo, 
			# adicionar uma competiçaõ anexada a uma época
			epo_id = self.request.get('epo_id')
				
			if epo_id: 
				epoca = Epoca.get_by_id(int(epo_id))
			else:
				try:
					epoca = Epoca.get_by_id(int(self.request.get('cmp_epoca_id')))
				except:
					pass
							
			if not epoca:
				error = u"Erro: Não encontrei época %s!" % self.request.get('cmp_epoca_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
			
			### LUGARES ### 
				
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
				
			numero_jornadas = 0
			try:
				numero_jornadas = int(self.request.get('cmp_numero_jornadas'))
			except:
				pass
						
			obj = Competicao(
				cmp_numero_visitas = 0,
				cmp_ultima_alteracao = date,
				cmp_nome = epoca.epo_nome+":"+self.request.get('cmp_tipo'),
				cmp_nome_completo = self.request.get('cmp_nome_completo'), 
				cmp_tipo = self.request.get('cmp_tipo'),
				cmp_link_zz = db.Link(self.request.get('cmp_link_zz')),
				cmp_link_foto = self.request.get('cmp_link_foto'),
				cmp_epoca = epoca,
				cmp_numero_jornadas = numero_jornadas,
				cmp_lugares_liga_campeoes = lugares_liga_campeoes,
				cmp_lugares_liga_europa = lugares_liga_europa,
				cmp_lugares_eliminatorias_liga_campeoes = lugares_eliminatorias_liga_campeoes,
				cmp_lugares_descida = lugares_descida
			)
			
			### PROPAGAR ALTERAÇOES ###
			epoca.epo_ultima_alteracao=date
			db.put([obj,epoca])

			memcache.set_multi({
				str(obj.key().id()):obj,
				str(epoca.key().id()):epoca}, 
			time=86400)
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)			
###########
# JORNADA #
###########
		
		elif objname == "jornada":
			
# sanitizar jornada 

			cmp_id = self.request.get('cmp_id')
			competicao = None
			
			if cmp_id: 
				competicao = Competicao.get_by_id(int(cmp_id))
			else:
				try:
					competicao = Competicao.get_by_id(int(self.request.get('jor_competicao_id')))
				except:
					pass
					
			if not competicao: 
				error = u"Erro: Não encontrei competição com id %s!" % self.request.get('jor_competicao_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			data = datetime.datetime.strptime(
				self.request.get('jor_data'), "%Y-%m-%d") if \
					self.request.get('jor_data') else None

# obj jornada #

			obj = Jornada(
				jor_numero_visitas = 0,
				jor_ultima_alteracao = date,
				jor_nome = competicao.cmp_nome+":"+self.request.get('jor_nome_curto'),
				jor_data = data.date(),
				jor_epoca = competicao.cmp_epoca,
				jor_competicao = competicao,
				jor_nome_curto = self.request.get('jor_nome_curto'),
				jor_nome_completo = self.request.get('jor_nome_completo'),
				jor_ordem = int(self.request.get('jor_ordem')),
				jor_link_zz = db.Link(self.request.get('jor_link_zz'))
			)	
			
			competicao.cmp_ultima_alteracao=date
			competicao.cmp_epoca.epo_ultima_alteracao=date
			db.put([obj,competicao,competicao.cmp_epoca])

			memcache.set_multi({
				str(obj.key().id()):obj,
				str(competicao.key().id()):competicao,
				str(competicao.cmp_epoca.key().id()):competicao.cmp_epoca}, 
			time=86400)

			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

########
# JOGO #
########
				
		elif objname == "jogo":

# sanitizar jogo
			jornada = None
			clube_casa = None
			clube_fora = None
			
			jor_id  = self.request.get('jor_id')
			if jor_id: 
				jornada = Jornada.get_by_id(int(jor_id))
			else:
				jornada = Jornada.all().filter("jor_nome = ", self.request.get('jog_jornada')).get()
			
			if not jornada:
				error = u"Erro: Não encontrei jornada %s!" % self.request.get('jog_jornada')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
			
			try:
				clube_casa = Clube.get_by_id(int(self.request.get('jog_clube1_id')))
			except:
				error = u"Erro: Não encontrei clube de casa com nome %s!" % \
				 self.request.get('jog_clube1_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			try:
				clube_fora = Clube.get_by_id(int(self.request.get('jog_clube2_id')))
			except:
				error = u"Erro: Não encontrei clube visitante com nome %s!" % self.request.get('jog_clube2_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
			
			# arbitro pode vir já com id, por exemplo na página edit de um árbitro pode-ser criar um jogo
			arb_id = self.request.get('arb_id')
			arbitro = None
			if arb_id: 
				arbitro = Arbitro.get_by_id(int(arb_id))
			else:
				try:
					arbitro = Arbitro.get_by_id(int(self.request.get('jog_arbitro_id')))
				except:
					arbitro = Arbitro.all().filter("arb_nome = ", 'jog_arbitro').get()
					
			list_link_sites = []
			
			for link_site in self.request.get_all('jog_link_sites'):
				if link_site != "":
					list_link_sites.append(db.Link(link_site))
			
			list_link_videos = []
			
			for link_video in self.request.get_all('jog_link_videos'):
				if link_video != "":
					list_link_videos.append(db.Text(link_video))

			data = datetime.datetime.strptime(self.request.get('jog_data'), "%Y-%m-%d %H:%M") if \
						self.request.get('jog_data') else None
# obj jogo 
			
			clubes = [] 
			if clube_casa:
				clubes.append(clube_casa.key())
			if clube_fora:
				clubes.append(clube_fora.key())

			obj = Jogo(
					jog_numero_visitas = 0,
					jog_ultima_alteracao = date,
					jog_nome = jornada.jor_nome+":"+clube_casa.clu_nome+":"+clube_fora.clu_nome,
					jog_epoca = jornada.jor_competicao.cmp_epoca,
					jog_competicao = jornada.jor_competicao,
					jog_jornada = jornada,
					jog_data = data,
					jog_clube1 = clube_casa,
					jog_clube2 = clube_fora,
					jog_clubes = clubes,
					jog_tactica_clube1 = self.request.get('jog_tactica_clube1'),
					jog_tactica_clube2 = self.request.get('jog_tactica_clube2'),
					jog_arbitro = arbitro if arbitro else None, 
					jog_golos_clube1 = int(self.request.get('jog_golos_clube1')) if \
						self.request.get('jog_golos_clube1') else None,
					jog_golos_clube2 = int(self.request.get('jog_golos_clube2')) if \
						self.request.get('jog_golos_clube2') else None,
					jog_link_sites = list_link_sites,
					jog_link_videos = list_link_videos,
					jog_comentario = self.request.get('jog_comentario')
			)
			
			objs = []
			memcache_objs = {}
			
			clube_casa.clu_ultima_alteracao=date 
			objs.append(clube_casa)
			memcache_objs[str(clube_casa.key().id())] = clube_casa
			clube_fora.clu_ultima_alteracao=date 
			memcache_objs[str(clube_fora.key().id())] = clube_fora
			objs.append(clube_fora)
			jornada.jor_ultima_alteracao=date
			memcache_objs[str(jornada.key().id())] = jornada
			objs.append(jornada)
			jornada.jor_competicao.cmp_ultima_alteracao=date
			memcache_objs[str(jornada.jor_competicao.key().id())] = jornada.jor_competicao
			objs.append(jornada.jor_competicao)
			jornada.jor_competicao.cmp_epoca.epo_ultima_alteracao=date
			memcache_objs[str(jornada.jor_competicao.cmp_epoca.key().id())] = jornada.jor_competicao.cmp_epoca
			objs.append(jornada.jor_competicao.cmp_epoca)
			if arbitro:
				arbitro.arb_ultima_alteracao=date
				objs.append(arbitro)

			objs.append(obj)
			db.put(objs)
			memcache_objs[str(obj.key().id())] = obj
			memcache.set_multi(memcache_objs, time=86400)
			
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

#########
# LANCE #
#########			
		
		elif objname == "lance":

# sanitanizar lance 

			jogo = None
			jog_id = self.request.get('jog_id')
			
			if jog_id:
				jogo = Jogo.get_by_id(int(jog_id))
			if not jogo: 
				jogo = Jogo.all().filter("jog_nome = ", self.request.get('lan_jogo')).get()
				
			if not jogo: 
				error = u"Erro: Não encontrei jogo %s!" % self.request.get('lan_jogo')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return

			list_link_sites = []
			
			for link_site in self.request.get_all('lan_link_sites'):
				if link_site != "":
					list_link_sites.append(db.Link(link_site))
			
			list_link_videos = []
			
			for link_video in self.request.get_all('lan_link_videos'):
				if link_video != "":
					list_link_videos.append(db.Text(link_video))

# obj single lance 

			minuto = None
			if self.request.get('lan_minuto'):
				minuto = int(self.request.get('lan_minuto'))

			obj = Lance(
				lan_numero_visitas = 0,
				lan_ultima_alteracao = date,
				lan_nome = jogo.jog_nome+":"+self.request.get('lan_numero'),
				lan_epoca = jogo.jog_jornada.jor_competicao.cmp_epoca,
				lan_competicao = jogo.jog_jornada.jor_competicao,				
				lan_jornada = jogo.jog_jornada,				
				lan_jogo = jogo,
				lan_data = jogo.jog_data,
				lan_arbitro = jogo.jog_arbitro, 
				lan_clube1 = jogo.jog_clube1,
				lan_clube2 = jogo.jog_clube2,
				lan_numero = int(self.request.get('lan_numero')),
				lan_minuto = minuto,
				lan_descricao = self.request.get('lan_descricao'),
				lan_classe =  int(self.request.get('lan_classe')),
				lan_link_sites =list_link_sites,
				lan_link_videos = list_link_videos,
				lan_comentario = self.request.get('lan_comentario')
			)

			objs = []
			memcache_objs = {}

			jogo.jog_ultima_alteracao=date 
			memcache_objs[str(jogo.key().id())] = jogo
			objs.append(jogo)
			jogo.jog_clube1.clu_ultima_alteracao=date 
			objs.append(jogo.jog_clube1)
			memcache_objs[str(jogo.jog_clube1.key().id())] = jogo.jog_clube1
			jogo.jog_clube2.clu_ultima_alteracao=date 
			memcache_objs[str(jogo.jog_clube2.key().id())] = jogo.jog_clube2
			objs.append(jogo.jog_clube2)
			jogo.jog_jornada.jor_ultima_alteracao=date
			memcache_objs[str(jogo.jog_jornada.key().id())] = jogo.jog_jornada
			objs.append(jogo.jog_jornada)
			jogo.jog_jornada.jor_competicao.cmp_ultima_alteracao=date
			memcache_objs[str(jogo.jog_jornada.jor_competicao.key().id())] = jogo.jog_jornada.jor_competicao
			objs.append(jogo.jog_jornada.jor_competicao)
			jogo.jog_jornada.jor_competicao.cmp_epoca.epo_ultima_alteracao=date

			memcache_objs[str(jogo.jog_jornada.jor_competicao.cmp_epoca.key().id())] = jogo.jog_jornada.jor_competicao.cmp_epoca
			objs.append(jogo.jog_jornada.jor_competicao.cmp_epoca)
			if jogo.jog_arbitro:
					jogo.jog_arbitro.arb_ultima_alteracao=date
					objs.append(jogo.jog_arbitro)
					memcache_objs[str( jogo.jog_arbitro.key().id())] = jogo.jog_arbitro

			objs.append(obj)

			db.put(objs)
			memcache_objs[str(obj.key().id())] =obj 
			memcache.set_multi(memcache_objs, time=86400)

			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

#########
# CLUBE #
#########
		
		elif objname == "clube":

			obj = Clube(
				clu_numero_visitas = 0,
				clu_ultima_alteracao = date,
				clu_nome_completo = self.request.get('clu_nome_completo'),
				clu_nome_curto = self.request.get('clu_nome_curto'),
				clu_nome = self.request.get('clu_nome'),
				clu_link_logo = self.request.get('clu_link_logo'),
				clu_link_zz = db.Link(self.request.get('clu_link_zz'))
			)
			
			obj.put()
			memcache.set_multi({str(obj.key().id()):obj}, time=86400)
				
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

###########
# JOGADOR #
###########

		elif objname == "jogador": 

# sanitizar jogador 
			
			clube = None
			posicao = []
			numero = None
						
			empty = True
			if self.request.get_all('jgd_posicao'):
				for pos in self.request.get_all('jgd_posicao'):
					if pos != "": 
						empty = False
						
			if not empty:
				for pos in self.request.get_all('jgd_posicao'):
					if pos != "":
						posicao.append(pos)
			
			try:
				clube = Clube.get_by_id(int(self.request.get('jgd_clube_actual_id')))
			except: 
				error = u"Erro: Não encontrei clube com if %s!" % \
				 self.request.get('jgd_clube_actual_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return

			try:
				numero = int(self.request.get('jgd_numero'))
			except:
				numero = 0

			epocas = []
			for epoca_id in self.request.get_all('jgd_epocas_id'):
				if epoca_id != "":
					epoca = None
					try:
						epoca = Epoca.get_by_id(int(epoca_id))
					except:
						pass
						#epoca = Epoca.all().filter("__key__ in", [db.Key(epoca_nome)]).get()
						
					if epoca:	
						epocas.append(epoca.key()) 

			# Por defeito, adiciona a época corrente ao novo jogador.
			if not epocas:
				epocas.append(config.EPOCA_CORRENTE.key()) 

# obj jogador 

			obj = Jogador(
				jgd_numero_visitas = 0,
				jgd_ultima_alteracao = date,
				jgd_nome = self.request.get('jgd_nome'),
				jgd_nome_completo = self.request.get('jgd_nome_completo'),
				jgd_numero = numero,
				jgd_link_foto = self.request.get('jgd_link_foto'),
				jgd_link_zz = db.Link(self.request.get('jgd_link_zz')),
				jgd_posicao = posicao,
				jgd_clube_actual = clube
			)
			
			clube.clu_ultima_alteracao = date

			db.put([obj,clube])

			# adicionar tb um CTJ
			ctj_obj = ClubeTemJogador(
				ctj_numero = numero,
				ctj_epocas = epocas,
				ctj_jogador = obj,
				ctj_clube = clube
			)
	
			db.put(ctj_obj)
				
			memcache.set_multi({
				str(clube.key().id()):clube, 
				str(obj.key().id()):obj}, 
			time=86400)
				
			flash_messages.append(u"%s %s adicionado." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
			flash_messages.append(u"%s %s adicionado." % (ctj_obj.kind(), ctj_obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

###########
# ARBITRO #
###########

		elif objname == "arbitro":

# obj #			
			obj = Arbitro(
				arb_numero_visitas = 0,
				arb_ultima_alteracao = date,
				arb_nome = self.request.get('arb_nome'),
				arb_link_foto = self.request.get('arb_link_foto'),
				arb_link_zz = db.Link(self.request.get('arb_link_zz'))
			)
		
			obj.put()
			memcache.set_multi({str(obj.key().id()):obj}, time=86400)
				
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

##############
# COMENTADOR #
##############
				
		elif objname == "comentador":
			
			# na página edit da fonte, posso criar comentadores já associados com uma fon_id
			fon_id = self.request.get('fon_id')
			if fon_id: 
				fonte = Fonte.get_by_id(int(fon_id))
			else:
				fonte = Fonte.all().filter("fon_nome = ", self.request.get('com_fonte')).get()
			
			if not fonte: 
				error = u"Erro: Não encontrei fonte com nome %s!" % self.request.get('com_fonte')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return 
				
			obj = Comentador(
				com_numero_visitas = 0,
				com_ultima_alteracao = date,
				com_nome = self.request.get('com_nome'),
				com_foto = self.request.get('com_foto'),
				com_fonte = fonte
			)
			obj.put()
			memcache.set_multi({str(obj.key().id()):obj}, time=86400)
			flash_messages.append(u"%s %s adicionado." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return
			
#########
# FONTE #
#########
			
		elif objname == "fonte":
			
			obj = Fonte(
				fon_numero_visitas = 0,
				fon_ultima_alteracao = date,
				fon_nome = self.request.get('fon_nome'),
				fon_link = db.Link(self.request.get('fon_link'))
			)
			obj.put()
			memcache.set_multi({str(obj.key().id()):obj}, time=86400)
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return 
			
# moléculas: estas podem ter um id anexado ou não.
# Por exemplo, em clube_tem_jogador, um clu_id=1 é para fazer um clube/edit?id=1
# um jgd_id=1 é para fazer um jogador/edit?id=1
# sem nenhum deles, é porque vem de uma list, e não vem anexado a nenhuma entidade

#####################
# CLUBE_TEM_JOGADOR #
#####################

		elif objname == "clube_tem_jogador": 

# sanitização clube_tem_jogador #
			
			clu_id = self.request.get('clu_id')
			jgd_id = self.request.get('jgd_id')
			
			clube = None
			jogador = None
			# ok, estamos a associar um jogador na página 'edit' de um clube
			if clu_id: 
				clube = Clube.get_by_id(int(clu_id))
			# ok, estamos a adicionar um clube na página 'edit' de um jogador
			if jgd_id:
				jogador = Jogador.get_by_id(int(jgd_id))
			
			# ok, estamos na página 'new' de um jogador_tem_clube, onde o clube e jogador vão 
			# ser introduzidos e é preciso validar antes
			if not clube:
				try:
					clube = Clube.get_by_id(int(self.request.get('ctj_clube_id')))
				except:
					pass
					
			if not clube: 
				error = u"Erro: Não encontrei clube com id %s!" % self.request.get('ctj_clube_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			if not jogador: 
				jogador = Jogador.all().filter("jgd_nome= ", self.request.get('ctj_jogador')).get()
				
			if not jogador: 
				error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get('ctj_jogador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
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

# obj clube_tem_jogador #
						
			# agora que está tudo sanitanizado, toca a inserir
			obj = ClubeTemJogador(
				ctj_clube = clube,
				ctj_jogador = jogador,
				ctj_epocas = epocas,
				ctj_numero = int(self.request.get('ctj_numero'))
			)
			
			clube.clu_ultima_alteracao = date
			jogador.jgd_ultima_alteracao = date
			db.put([obj, jogador, clube])
			memcache.set_multi({str(clube.key().id()):clube, str(jogador.key().id()):jogador}, time=86400)
				
			flash_messages.append(u"%s %s adicionado." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return
				
#########################
# CLUBE_JOGA_COMPETICAO #
#########################
		
		elif objname == "clube_joga_competicao": 
			
# sanitização clube_joga_competicao #
			
			clu_id = self.request.get('clu_id')
			cmp_id = self.request.get('cmp_id')
			clube = None
			competicao = None
			
			if clu_id: 
				clube = Clube.get_by_id(int(clu_id))
			if cmp_id:
				competicao = Competicao.get_by_id(int(cmp_id))
			
			# ok, estamos na página 'new' de um jogador_tem_clube, onde o clube e jogador vão 
			# ser introduzidos e é preciso validar antes
			if not clube:
				try:
					clube = Clube.get_by_id(int(self.request.get('cjc_clube_id')))
				except:
					pass
					
			if not clube: 
				error = u"Erro: Não encontrei clube com id %s!" % self.request.get('cjc_clube_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			if not competicao: 
				# competicao vem como epoca:tipo
				competicao = Competicao.get_by_id(int(self.request.get('cjc_competicao_id')))
			
			if not competicao: 
				error = u"Erro: Não encontrei competicao com nome %s!" % self.request.get('cjc_competicao_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return

# obj clube_joga_competicao #
			
			cjc_classificacao_anterior = 0
			try:
				cjc_classificacao_anterior = int(self.request.get('cjc_classificacao_anterior'))
			except:
				cjc_classificacao_anterior = 0
				
			obj = ClubeJogaCompeticao(
				cjc_clube = clube,
				cjc_competicao = competicao,
				cjc_classificacao_anterior = cjc_classificacao_anterior
			)
			clube.clu_ultima_alteracao = date
			competicao.cmp_ultima_alteracao = date
			db.put([obj, competicao, clube])
			memcache.set_multi({str(clube.key().id()):clube, str(competicao.key().id()):competicao}, time=86400)
				
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

#####################
# JOGADOR_JOGA_JOGO #
#####################
			
		elif objname == "jogador_joga_jogo": 

# sanitizar jogador_joga_jogo # 

			jgd_id = self.request.get('jgd_id')
			jog_id = self.request.get('jog_id')
			clu_id = self.request.get('clu_id')
			
			jogo = None
			jogador = None
			clube = None
			
				# jgd_id and not jog_id: estamos a associar um jogo na página 'edit' de um jogador
				# jog_id and not jgd_id:, estamos a adicionar um jogador na página 'edit' de um jogo
				# jog_id e jgd_id: na página de jogo edit (com jog_id), temos uma select box que dá o id do jogador (jgd_id)
			if jgd_id: 
				jogador = Jogador.get_by_id(int(jgd_id))
			if jog_id:
				jogo = Jogo.get_by_id(int(jog_id))
			if clu_id:
				clube = Clube.get_by_id(int(clu_id))
			
			# ok, estamos na página 'new' de um jogador_joga_jogo, onde o
			# jogador e jogo vão ser introduzidos e é preciso validar antes
			if not jogador:
				jogador = Jogador.all().filter("jgd_nome= ", self.request.get('jjj_jogador')).get()
					
			if not jogador: 
				error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get('jjj_jogador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			if not jogo: 
				# jogo não tem nome, vamos apanhá-lo com ep_nome:cmp_tipo:jor_nome_curto:clube1_sigla:clube2_sigla 
				jogo = Jogo.all().filter("jog_nome = ", self.request.get('jjj_jogo')).get()
				
			if not jogo: 
				error = u"Erro: Não encontrei jogo %s!" % self.request.get('jjj_jogo')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			if not clube:
				try:
					clube = Clube.get_by_id(int(self.request.get('jjj_clube_id')))
				except:
					pass
						
			if not clube: 
				error = u"Erro: Não encontrei clube com id %s!" % self.request.get('jjj_clube_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return

			amarelo = self.request.get('jjj_amarelo_minuto')
			if amarelo:
				amarelo = int(amarelo)
			else:
				amarelo = None
					
			damarelo = self.request.get('jjj_duplo_amarelo_minuto')
			if damarelo:
				damarelo = int(damarelo)
			else:
				damarelo = None
					
			vermelho = self.request.get('jjj_vermelho_minuto')
			if vermelho:
				vermelho = int(vermelho)
			else:
				vermelho = None
					
			entrada = self.request.get('jjj_substituicao_entrada')
			if entrada:
				entrada = int(entrada)
			else:
				entrada = None
					
			saida = self.request.get('jjj_substituicao_saida')
			if saida:
				saida = int(saida)
			else:
				saida = None

# obj jogador_joga_jogo #
				
			# agora que está tudo sanitanizado, toca a inserir
			obj = JogadorJogaJogo(
					jjj_jogador = jogador,
					jjj_jogo = jogo,
					jjj_clube = clube,
					jjj_posicao = self.request.get('jjj_posicao'), 
					jjj_amarelo_minuto = amarelo,
					jjj_duplo_amarelo_minuto = damarelo,
					jjj_vermelho_minuto = vermelho,
					jjj_substituicao_entrada = entrada,
					jjj_substituicao_saida = saida	
			)		
							
			list = []
			list_tipos = []
				
			list_tipos_x = self.request.get_all('jjj_golos_tipos')
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
				
			clube.clu_ultima_alteracao = date
			jogador.jgd_ultima_alteracao = date
			jogo.jog_ultima_alteracao = date
			db.put([obj, jogador, jogo, clube])

			memcache.set_multi({
					str(clube.key().id()):clube, 
					str(jogador.key().id()):jogador,
					str(jogo.key().id()):jogo
				}, time=86400)
		
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return				

############################
# COMENTADOR_COMENTA_LANCE #
############################			
			
		elif objname == "comentador_comenta_lance": 
	
# sanitização comentador_comenta_lance #
			
			com_id = self.request.get('com_id')
			lan_id = self.request.get('lan_id')
			comentador = None
			lance = None
			
			if com_id: 
				comentador = Comentador.get_by_id(int(com_id))
			if lan_id:
				lance = Lance.get_by_id(int(lan_id))

			if not comentador:
				comentador = Comentador.get_by_id(int(self.request.get('ccl_comentador_id')))
			if not comentador: 
				error = u"Erro: Não encontrei comentador com id %s!" % self.request.get('ccl_comentador_id')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			if not lance: 
				lance = Lance.all().filter("lan_nome = ",self.request.get('ccl_lance')).get()
				
			if not lance: 
				error = u"Erro: Não encontrei lance %s!" % self.request.get('ccl_lance')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return

# obj comentador_comenta_lance #

			obj = ComentadorComentaLance(
				ccl_comentador = comentador,
				ccl_lance = lance,
				ccl_descricao = self.request.get('ccl_descricao'),
				ccl_decisao = int(self.request.get('ccl_decisao'))
			)
			
			objs = []
			memcache_objs = {}
			
			comentador.com_ultima_alteracao = date
			objs.append(comentador)	

			lance.lan_ultima_alteracao = date
			objs.append(lance)
			memcache_objs[str(lance.key().id())] = lance

			objs.append(obj)
			memcache_objs[str(obj.key().id())] = obj
			
			lance.lan_jogo.jog_ultima_alteracao=date 
			memcache_objs[str(lance.lan_jogo.key().id())] = lance.lan_jogo
			objs.append(lance.lan_jogo)
			lance.lan_jogo.jog_clube1.clu_ultima_alteracao=date 
			objs.append(lance.lan_jogo.jog_clube1)
			memcache_objs[str(lance.lan_jogo.jog_clube1.key().id())] = lance.lan_jogo.jog_clube1
			lance.lan_jogo.jog_clube2.clu_ultima_alteracao=date 
			memcache_objs[str(lance.lan_jogo.jog_clube2.key().id())] = lance.lan_jogo.jog_clube2
			objs.append(lance.lan_jogo.jog_clube2)
			lance.lan_jornada.jor_ultima_alteracao=date
			memcache_objs[str(lance.lan_jornada.key().id())] = lance.lan_jornada
			objs.append(lance.lan_jornada)
			lance.lan_competicao.cmp_ultima_alteracao=date
			memcache_objs[str(lance.lan_competicao.key().id())] = lance.lan_competicao
			objs.append(lance.lan_competicao)
			lance.lan_epoca.epo_ultima_alteracao=date
			memcache_objs[str(lance.lan_epoca.key().id())] = lance.lan_epoca
			objs.append(lance.lan_epoca)
			if lance.lan_jogo.jog_arbitro:
				lance.lan_jogo.jog_arbitro.arb_ultima_alteracao=date
				objs.append(lance.lan_jogo.jog_arbitro)
				memcache_objs[str( lance.lan_jogo.jog_arbitro.key().id())] = lance.lan_jogo.jog_arbitro

			db.put(objs)
			memcache.set_multi(memcache_objs, time=86400)

			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

####################
# JOGADOR_EM_LANCE #
####################
			
		elif objname == "jogador_em_lance": 

# sanitização jogador_em_lance #
			
			jgd_id = self.request.get('jgd_id')
			lan_id = self.request.get('lan_id')
			lance = None
			jogador = None
			
			# ok, estamos a associar um lance na página 'edit' de um jogador
			if jgd_id: 
				jogador = Jogador.get_by_id(int(jgd_id))
			# ok, estamos a adicionar um comentador na página 'edit' de um lance
			if lan_id:
				lance = Lance.get_by_id(int(lan_id))
			# ok, estamos na página 'new' de um jogador_joga_jogo, onde o jogador e jogo vão 
			# ser introduzidos e é preciso validar antes
			if not jogador:
				jogador = Jogador.all().filter("jgd_nome= ", self.request.get('jel_jogador')).get()
			
			if not jogador: 
				error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get('jel_jogador')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
				
			if not lance: 
				# lance não tem nome, vamos apanhá-lo com jogo (ep_nome:cmp_tipo:jor_nome_curtp:clube1_sigla:clube2_sigla) e numero
				lance = Lance.all().filter("lan_nome = ",self.request.get('ccl_lance')).get()

				
			if not lance: 
				error = u"Erro: Não encontrei lance %s!" % self.request.get('jel_lance')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return

# obj jogador_em_lance #
				
			# agora que está tudo sanitanizado, toca a inserir
			obj = JogadorEmLance(
				jel_jogador = jogador,
				jel_lance = lance,
				jel_papel = self.request.get("jel_papel")
			)
			
			# não me apetece sincronizar os parentes de lance...
			jogador.jgd_ultima_alteracao = date
			lance.lan_ultima_alteracao = date
			db.put(obj, lance, jogador)
			memcache.set_multi({
				str(jogador.key().id()):jogador,
				str(lance.key().id()):lance
			}, time=86400)
				
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

######################
# ACUMULADOR JORNADA #
######################
			
		elif objname == "acumulador_jornada": 

			jornada = None
			
			jor_id  = self.request.get('jor_id')
			if jor_id: 
				jornada = Jornada.get_by_id(int(jor_id))
			else:
				jornada = Jornada.all().filter("jor_nome = ", self.request.get('acuj_jornada')).get()
			
			if not jornada:
				error = u"Erro: Não encontrei jornada %s!" % self.request.get('acuj_jornada')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
			
			stats = acumulador_jornada.gera(jornada)
			
			versao = None
			try:
				versao = int(self.request.get('acuj_versao'))
			except:
				versao = config.VERSAO_ACUMULADOR
				
			obj = AcumuladorJornada.all().filter("acuj_jornada = ", jornada).filter("acuj_versao = ", versao).get()
			if not obj:
				obj = AcumuladorJornada(
					acuj_jornada=jornada, 
					acuj_versao=versao,
					acuj_competicao = jornada.jor_competicao,
					acuj_epoca = jornada.jor_competicao.cmp_epoca
				)

			obj.acuj_epoca = jornada.jor_competicao.cmp_epoca
			obj.acuj_competicao = jornada.jor_competicao
			obj.acuj_jornada = jornada
			obj.acuj_date = date
			obj.acuj_content = stats
			obj.put()
			
			# os acumuladores não são chamados por ID, mas por namespaces/jor-cmp-epo 
			memcache.set(u"acumulador-%s-%s" % (jornada, str(versao)), obj, time=86400)
			
			flash_messages.append(u"%s %s adicionada." % (obj.kind(), obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

#########################
# ACUMULADOR COMPETICAO #
#########################
			
		elif objname == "acumulador_competicao": 
			
			competicao = None

			cmp_id  = self.request.get('cmp_id')

			acuc_basico = self.request.get('acuc_basico')
			acuc_classificacao = self.request.get('acuc_classificacao')
			acuc_tabela_icc = self.request.get('acuc_tabela_icc')
			acuc_icc = self.request.get('acuc_icc')
			acuc_top_arbitros = self.request.get('acuc_top_arbitros')
			acuc_top_jogos = self.request.get('acuc_top_jogos')
			acuc_top_jogadores = self.request.get('acuc_top_jogadores')
			acuc_top_clubes = self.request.get('acuc_top_clubes')

			if cmp_id: 
				competicao = Competicao.get_by_id(int(cmp_id))
			else:
				competicao = Competicao.all().filter("cmp_nome = ", self.request.get("acuc_competicao")).get()
			
			if not competicao:
				error = u"Erro: Não encontrei competição %s!" % self.request.get('acuc_competicao')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
			
			stats = acumulador_competicao.gera(competicao, acuc_basico, 
				acuc_classificacao, acuc_tabela_icc, acuc_icc, acuc_top_arbitros,
				acuc_top_jogos, acuc_top_jogadores, acuc_top_clubes)
			
			versao = None
			try:
				versao = int(self.request.get('acuc_versao'))
			except:
				versao = config.VERSAO_ACUMULADOR	

### ACU_BASICO 

			if acuc_basico == "on":
					obj = addToAcumuladorCompeticao("arbitro", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "arbitro") ) 

					obj = addToAcumuladorCompeticao("jogo", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "jogo") ) 

					obj = addToAcumuladorCompeticao("jogador", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "jogador") ) 

					obj = addToAcumuladorCompeticao("clube", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "clube") ) 

### TOP_ARBITROS 

			if acuc_top_arbitros == "on":
					obj = addToAcumuladorCompeticao("top_arbitros", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_arbitros") ) 

### TOP_CLUBES 

			if acuc_top_clubes == "on":
					obj = addToAcumuladorCompeticao("top_clubes", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_clubes") ) 

### TOP_JOGOS 

			if acuc_top_jogos == "on":
					obj = addToAcumuladorCompeticao("top_jogos", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_jogos") ) 

### TOP_JOGADORES 

			if acuc_top_jogadores == "on":
					obj = addToAcumuladorCompeticao("top_jogadores", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_jogadores") ) 

### CLASSIFICACAO 

			if acuc_classificacao == "on":
				obj = addToAcumuladorCompeticao("classificacao_real", versao, competicao, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "classificacao_real") ) 

				obj = addToAcumuladorCompeticao("classificacao_virtual", versao, competicao, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "classificacao_virtual") )

### MATRIZ 

			if acuc_tabela_icc == "on":
					obj = addToAcumuladorCompeticao("tabela_icc", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (competicao, "tabela_icc") ) 

### ICC 

			if acuc_icc == "on":
					obj = addToAcumuladorCompeticao("icc", versao, competicao, stats, date)
					flash_messages.append(u"%s, namespace %s adicionado" % (competicao, "icc") ) 

			
			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return

####################
# ACUMULADOR EPOCA #
####################
			
		elif objname == "acumulador_epoca": 
			
			epoca = None

			epo_id  = self.request.get('epo_id')

			acue_basico = self.request.get('acue_basico')
			acue_tabela_icc = self.request.get('acue_tabela_icc')
			acue_icc = self.request.get('acue_icc')
			acue_top_arbitros = self.request.get('acue_top_arbitros')
			acue_top_jogos = self.request.get('acue_top_jogos')
			acue_top_jogadores = self.request.get('acue_top_jogadores')
			acue_top_clubes = self.request.get('acue_top_clubes')

			if epo_id: 
				epoca = Epoca.get_by_id(int(epo_id))
			else:
				epoca = Epoca.all().filter("epo_nome= ", self.request.get('acue_epoca')).get()
			
			if not epoca:
				error = u"Erro: Não encontrei epoca %s!" % self.request.get('acue_epoca')
				logging.error(error)
				memcache.set(str(new_sid), error, namespace="flash")
				self.add_sid_to_cookie(new_sid)
				self.redirect(referer)
				return
			
			stats = acumulador_epoca.gera(epoca, acue_basico, 
				acue_tabela_icc, acue_icc, acue_top_arbitros,
				acue_top_jogos, acue_top_jogadores, acue_top_clubes)
			
			versao = None
			try:
				versao = int(self.request.get('acue_versao'))
			except:
				versao = config.VERSAO_ACUMULADOR
			
			if acue_basico == "on":
				obj = addToAcumuladorEpoca("arbitro", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "arbitro") ) 

				obj = addToAcumuladorEpoca("jogo", versao, epoca, stats,  date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "jogo") ) 

				obj = addToAcumuladorEpoca("jogador", versao, epoca, stats,  date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "jogador") ) 

				obj = addToAcumuladorEpoca("clube", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "clube") ) 

### TOP_ARBITROS 

			if acue_top_arbitros == "on":
				obj = addToAcumuladorEpoca("top_arbitros", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_arbitros") ) 

### TOP_CLUBES 

			if acue_top_clubes == "on":
				obj = addToAcumuladorEpoca("top_clubes", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_clubes") ) 

### TOP_JOGOS 

			if acue_top_jogos == "on":
				obj = addToAcumuladorEpoca("top_jogos", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_jogos") ) 

### TOP_JOGADORES 

			if acue_top_jogadores == "on":
				obj = addToAcumuladorEpoca("top_jogadores", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "top_jogadores") ) 


### MATRIZ 

			if acue_tabela_icc == "on":
				obj = addToAcumuladorEpoca("tabela_icc", versao,  epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "tabela_icc") ) 

### ICC 

			if acue_icc == "on":
				addToAcumuladorEpoca("icc", versao, epoca, stats, date)
				flash_messages.append(u"%s, namespace %s adicionado" % (obj.kind(), "icc") ) 

			memcache.set(str(new_sid), "<BR>".join(flash_messages), namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)
			return
	
	# def processTasks(self):	
	# 	task_prefixes = self.request.get_all("task_prefix")
	# 	if task_prefixes:
	# 		for task_prefix in task_prefixes:
	# 			task_checkbox = self.request.get(task_prefix+"_checkbox")
	# 			task_url = self.request.get_all(task_prefix+"_url")
	# 			task_countdown = int(self.request.get(task_prefix+"_countdown"))
	# 			task_param = self.request.get(task_prefix+"_param")
	# 			
	# 			message = None
	# 			# se é para lançar task
	# 			if task_checkbox == "on":
	# 				# o URL é diferente Precisa do novo ID.
	# 				for url in task_url:
	# 					message = CacheRegenerator().add(url, 
	# 						task_countdown, task_param)
	# 					flash_messages.append(message)
	# 					logging.info(message)
	# 		

def addToAcumuladorCompeticao(string, versao, competicao, stats, date):
	obj = AcumuladorCompeticao.all().filter("acuc_competicao = ", competicao).filter("acuc_versao =", versao).filter("acuc_namespace =", string).get()
	if not obj:
		obj = AcumuladorCompeticao(
		acuc_competicao = competicao, 
		acuc_epoca = competicao.cmp_epoca,
		acuc_namespace = string,
		acuc_versao = versao,
		acuc_date = date,
		acuc_content = {string : stats[string]}
	)
	else:
		obj.acuc_date = date
		obj.acuc_content = {string : stats[string]}
		
	logging.info(u"Saving AcumuladorCompeticao for %s, v%s, %s" % (competicao, versao, string))
	obj.put()
	# os acumuladores não são chamados por ID, mas por namespaces/jor-cmp-epo 
	memcache.set(u"acumulador-%s-%s" % (competicao, str(versao)), obj, namespace=string, time=86400)
	return obj
	
def addToAcumuladorEpoca(string, versao, epoca, stats, date):
	obj = AcumuladorEpoca.all().filter("acue_epoca = ", epoca).filter("acue_versao = ", versao).filter("acue_namespace =", string).get()
	if not obj:
		obj = AcumuladorEpoca(
		acue_epoca = epoca,
		acue_namespace = string,
		acue_versao = versao,
		acue_date = date,
		acue_content = {string : stats[string]}
		)
	else:
		obj.acue_date = date
		obj.acue_content = {string : stats[string]}

	obj.put()
	# os acumuladores não são chamados por ID, mas por namespaces/jor-cmp-epo 
	memcache.set(u"acumulador-%s-%s" % (epoca, str(versao)), obj, namespace=string, time=86400)
	return obj
