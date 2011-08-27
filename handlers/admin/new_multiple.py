# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db

import os
import datetime
import logging
import re
import config 
import sys
import lib.mymemcache

from classes import *
from externals.paging import *
from lib.myhandler import MyHandler
from lib import acumulador_jornada
from lib import acumulador_competicao
from lib import acumulador_epoca

class NewMultiple(MyHandler):
	
	def post(self, objname):

		referer = os.environ['HTTP_REFERER'] 
		
		# prefixo par aidentificar os parâmetros
		prefix = self.request.get("prefix")
		# número de parâmetros
		number = int(self.request.get("number"))
		new_sid = mymemcache.generate_sid()
	
		flash_messages = []
		date = datetime.datetime.now()
		
		objs = []
		memcache_objs = {}
		objs_adicionados = 0

#########
# EPOCA #
#########	
			
		if objname == "epoca": 
	
			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return

##############
# COMPETICAO #
##############

		elif objname == "competicao": 
			
			# PARA NOVAS COMPETIÇÕES ASSOCIADAS A UMA ÉPOCA 
			epo_id = self.request.get('epo_id')
			epoca_id = None	
			
			if epo_id: 
				epoca_id = Epoca.get_by_id(int(epo_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					epoca = None
					if epoca_id:
						epoca = epoca_id
					else:
						try:
							epoca = Epoca.get_by_id(int(self.request.get(prefix+str(index)+'_epoca_id')))
						except:
							pass

					if not epoca:
						error = u"Erro: Não encontrei época %s!" % self.request.get(prefix+str(index)+'_epoca')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
					
					lugares_liga_campeoes = []
					empty = True
					if self.request.get_all(prefix+str(index)+'_lugares_liga_campeoes'):
						for item in self.request.get_all(prefix+str(index)+'_lugares_liga_campeoes'):
							if item != "": 
								empty = False
						
					if not empty:
						for item in self.request.get_all(prefix+str(index)+'_lugares_liga_campeoes'):
							if item != "":
								lugares_liga_campeoes.append(int(item))

					lugares_liga_europa = []
					empty = True
					if self.request.get_all(prefix+str(index)+'_lugares_liga_europa'):
						for item in self.request.get_all(prefix+str(index)+'_lugares_liga_europa'):
							if item != "": 
								empty = False
						
					if not empty:
						for item in self.request.get_all(prefix+str(index)+'_lugares_liga_europa'):
							if item != "":
								lugares_liga_europa.append(int(item))

					lugares_eliminatorias_liga_campeoes = []
					empty = True
					if self.request.get_all(prefix+str(index)+'_lugares_eliminatorias_liga_campeoes'):
						for item in self.request.get_all(prefix+str(index)+'_lugares_eliminatorias_liga_campeoes'):
							if item != "": 
								empty = False
						
					if not empty:
						for item in self.request.get_all(prefix+str(index)+'_lugares_eliminatorias_liga_campeoes'):
							if item != "":
								lugares_eliminatorias_liga_campeoes.append(int(item))

					lugares_descida = []
					empty = True
					if self.request.get_all(prefix+str(index)+'_lugares_descida'):
						for item in self.request.get_all(prefix+str(index)+'_lugares_descida'):
							if item != "": 
								empty = False
						
					if not empty:
						for item in self.request.get_all(prefix+str(index)+'_lugares_descida'):
							if item != "":
								lugares_descida.append(int(item))
				
					numero_jornadas = 0
					try:
						numero_jornadas = int(self.request.get(prefix+str(index)+'_numero_jornadas'))
					except:
						pass
				
					competicao = Competicao(
						cmp_numero_visitas = 0,
						cmp_ultima_alteracao = date,
						cmp_nome =  epoca.epo_nome+":"+self.request.get(prefix+str(index)+'_tipo'),
						cmp_nome_completo = self.request.get(prefix+str(index)+'_nome_completo'), 
						cmp_tipo = self.request.get(prefix+str(index)+'_tipo'),
						cmp_link_zz = db.Link(self.request.get(prefix+str(index)+'_link_zz')),
						cmp_link_foto = self.request.get(prefix+str(index)+'_link_foto'),
						cmp_epoca = epoca,
						cmp_numero_jornadas = numero_jornadas,
						cmp_lugares_liga_campeoes = lugares_liga_campeoes,
						cmp_lugares_liga_europa = lugares_liga_europa,
						cmp_lugares_eliminatorias_liga_campeoes = lugares_eliminatorias_liga_campeoes,
						cmp_lugares_descida = lugares_descida
					)
			
					### PROPAGAR ALTERAÇOES ###
					epoca.epo_ultima_alteracao=date
					if epoca in objs:
						objs.remove(epoca)
					objs.append(epoca)
					memcache_objs[str(epoca.key().id())] = epoca
					
					objs.append(competicao)
					objs_adicionados += 1

			db.put(objs)
			
			for obj in objs:
				edit_type = None
				if obj.kind() == "Competicao":
					edit_type = "adicionada"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total adicionados: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
###########
# JORNADA #
###########

		elif objname == "jornada": 
			
			# PARA NOVAS JORNADAS 
			cmp_id = self.request.get('cmp_id')
			competicao_id = None	
			
			if cmp_id: 
				competicao_id = Competicao.get_by_id(int(cmp_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					competicao = None
					if competicao_id:
						competicao = competicao_id
					else:
						try:
							competicao = Competicao.get_by_id(int(self.request.get(prefix+str(index)+'_competicao_id')))
						except:
							pass

					if not competicao:
						error = u"Erro: Não encontrei competicao com id %s!" % self.request.get(prefix+str(index)+'_competicao_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

					data = datetime.datetime.strptime(
						self.request.get(prefix+str(index)+'_data'), "%Y-%m-%d") if \
						self.request.get(prefix+str(index)+'_data') else None

					jornada = Jornada(
						jor_numero_visitas = 0,
						jor_ultima_alteracao = date,
						jor_nome = competicao.cmp_nome+":"+self.request.get(prefix+str(index)+'_nome_curto'),
						jor_data = data.date(),
						jor_epoca = competicao.cmp_epoca,
						jor_competicao = competicao,
						jor_nome_curto = self.request.get(prefix+str(index)+'_nome_curto'),
						jor_nome_completo = self.request.get(prefix+str(index)+'_nome_completo'),
						jor_ordem = int(self.request.get(prefix+str(index)+'_ordem')),
						jor_link_zz = db.Link(self.request.get(prefix+str(index)+'_link_zz'))
					)	
					
					competicao.cmp_ultima_alteracao=date
					competicao.cmp_epoca.epo_ultima_alteracao=date
					
					if competicao.cmp_epoca in objs:
						objs.remove(competicao.cmp_epoca)
					objs.append(competicao.cmp_epoca)
					memcache_objs[str(competicao.cmp_epoca.key().id())] = competicao.cmp_epoca
					
					if competicao in objs:
						objs.remove(competicao)
					objs.append(competicao)
					memcache_objs[str(competicao.key().id())] = competicao
						
					objs.append(jornada)
					objs_adicionados += 1

			db.put(objs)

			for obj in objs:
				edit_type = None
				if obj.kind() == "Jornada":
					edit_type = "adicionada"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))			
########
# JOGO #
########

		elif objname == "jogo": 
			# PARA NOVOS JOGOS ASSOCIADAS A UMA JORNADA 
			jor_id = self.request.get('jor_id')
			jornada_id = None	
			
			if jor_id: 
				jornada_id = Jornada.get_by_id(int(jor_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					jornada = None
					clube_casa = None
					clube_fora = None
					arbitro = None
					clubes = []
 
					if jornada_id:
						jornada = jornada_id
					else:
						jornada = Jornada.all().filter("jor_nome = ", self.request.get(prefix+str(index)+'_jornada')).get()

					if not jornada:
						error = u"Erro: Não encontrei jornada %s!" % self.request.get(prefix+str(index)+'_jornada')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

					data = datetime.datetime.strptime(
						self.request.get(prefix+str(index)+'_data'), "%Y-%m-%d %H:%M") if \
						self.request.get(prefix+str(index)+'_data') else None

					try:
						clube_casa = Clube.get_by_id(int(self.request.get(prefix+str(index)+'_clube1_id')))
					except:
						error = u"Erro: Não encontrei clube de casa com id %s!" % \
						self.request.get(prefix+str(index)+'_clube1_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
				
					try:
						clube_fora = Clube.get_by_id(int(self.request.get(prefix+str(index)+'_clube2_id')))
					except:
						error = u"Erro: Não encontrei clube visitante com nome %s!" % self.request.get(prefix+str(index)+'_clube2_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
			
						# arbitro pode vir já com id, por exemplo na página edit de um árbitro pode-ser criar um jogo
					try:
						arbitro = Arbitro.get_by_id(int(self.request.get(prefix+str(index)+'_arbitro_id')))
					except:
						pass

					list_link_sites = []
					empty = True
					if self.request.get_all(prefix+str(index)+'_link_sites'):
						for item in self.request.get_all(prefix+str(index)+'_link_sites'):
							if item != u"": 
								empty = False
			
					if not empty:
						for link_site in self.request.get_all(prefix+str(index)+'_link_sites'):
							if link_site != "":
								list_link_sites.append(db.Link(link_site))
			
					list_link_videos = []
					empty = True
					if self.request.get_all(prefix+str(index)+'_link_videos'):
						for item in self.request.get_all(prefix+str(index)+'_link_videos'):
							if item != u"": 
								empty = False
					
					if not empty:
						for link_video in self.request.get_all(prefix+str(index)+'_link_videos'):
							if link_video != "":
								list_link_videos.append(db.Text(link_video))
			
				
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
					jog_tactica_clube1 = self.request.get(prefix+str(index)+'_tactica_clube1'),
					jog_tactica_clube2 = self.request.get(prefix+str(index)+'_tactica_clube2'),
					jog_golos_clube1 = int(self.request.get(prefix+str(index)+'_golos_clube1')) if \
						self.request.get(prefix+str(index)+'_golos_clube1') else None,
					jog_golos_clube2 = int(self.request.get(prefix+str(index)+'_golos_clube2')) if \
						self.request.get(prefix+str(index)+'_golos_clube2') else None,
					jog_link_sites = list_link_sites,
					jog_link_videos = list_link_videos,
					jog_comentario = self.request.get(prefix+str(index)+'_comentario')
					)
						
					if arbitro:
						obj.jog_arbitro = arbitro
	
					clube_casa.clu_ultima_alteracao = date
					clube_fora.clu_ultima_alteracao = date
					jornada.jor_competicao.cmp_epoca.epo_ultima_alteracao = date
					jornada.jor_competicao.cmp_ultima_alteracao = date
					jornada.jor_ultima_alteracao = date

					if clube_casa in objs:
						objs.remove(clube_casa)
					objs.append(clube_casa)	
					memcache_objs[str(clube_casa.key().id())] = clube_casa

					if clube_fora in objs:
						objs.remove(clube_fora)
					objs.append(clube_fora)	
					memcache_objs[str(clube_fora.key().id())] = clube_fora

					if jornada.jor_competicao.cmp_epoca in objs:
						objs.remove(jornada.jor_competicao.cmp_epoca)
					objs.append(jornada.jor_competicao.cmp_epoca)
					memcache_objs[str(jornada.jor_competicao.cmp_epoca.key().id())] = jornada.jor_competicao.cmp_epoca
					
					if jornada.jor_competicao in objs:
						objs.remove(jornada.jor_competicao)
					objs.append(jornada.jor_competicao)
					memcache_objs[str(jornada.jor_competicao.key().id())] = jornada.jor_competicao

					if jornada in objs:
						objs.remove(jornada)
					objs.append(jornada)
					memcache_objs[str(jornada.key().id())] = jornada

					objs.append(obj)
					objs_adicionados += 1
					
					if arbitro:
						arbitro.arb_ultima_alteracao = date
						if arbitro in objs:
							objs.remove(arbitro)
						objs.append(arbitro)
						memcache_objs[str(arbitro.key().id())] = arbitro

			db.put(objs)
			for obj in objs:
				edit_type = None
				if obj.kind() == "Jogo":
					edit_type = "adicionado"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))			
#########
# LANCE #
#########

###
		
		elif objname == "lance":

			jogo = None
			jog_id = self.request.get('jog_id')

			number_jels = int(self.request.get("number_jels"))
			number_ccls = int(self.request.get("number_ccls"))
				
			# PARA NOVOS LANCES ASSOCIADAS A UM JOGO 
			jog_id = self.request.get('jog_id')
			jogo_id = None	
			
			if jog_id: 
				jogo_id = Jogo.get_by_id(int(jog_id))

			jogo = None
			if jogo_id:
				jogo = jogo_id
			else:
				# vamos assumir que todos os lances pertencem a um jogo!
				jogo = Jogo.all().filter("jog_nome = ", self.request.get('lan_jogo')).get()

			ccls_adicionados = 0
			jels_adicionados = 0

			for index in range(number):
				
				lance_obj = None
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# fail fast - ainda posso apanhar jogos em "criar n lances"
					if not jogo:
						jogo = Jogo.all().filter("jog_nome = ", self.request.get(prefix+str(index)+'_jogo')).get()
						
					if not jogo:
						error = u"Erro: Não encontrei jogo %s!" % self.request.get(prefix+str(index)+'lan_jogo')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
					
					# ler variáveis de lance
					lance_numero = self.request.get(prefix+str(index)+"_numero")
					lance_minuto = self.request.get(prefix+str(index)+"_minuto")
					lance_classe = int(self.request.get(prefix+str(index)+"_classe"))
					lance_descricao = self.request.get(prefix+str(index)+"_descricao")
					
					lance_link_sites = []

					for lance_link_site in self.request.get_all(prefix+str(index)+"_link_sites"):
						if lance_link_site != "":
							lance_link_sites.append(db.Link(lance_link_site))
					lance_link_videos = []

					for lance_link_video in self.request.get_all(prefix+str(index)+"_link_videos"):
						if lance_link_video != "":
							lance_link_videos.append(db.Text(lance_link_video))
					
# OBJ MULTIPLE LANCES - LANCE
					minuto = 0
					if lance_minuto:
						minuto = int(lance_minuto)
						
					lance_obj = Lance(
							lan_numero_visitas = 0,
							lan_ultima_alteracao = date,
							lan_nome = jogo.jog_nome+":"+str(lance_numero),
							lan_epoca = jogo.jog_jornada.jor_competicao.cmp_epoca,
							lan_competicao = jogo.jog_jornada.jor_competicao,				
							lan_jornada = jogo.jog_jornada,				
							lan_jogo = jogo,
							lan_data = jogo.jog_data,
							lan_arbitro = jogo.jog_arbitro, 
							lan_clube1 = jogo.jog_clube1,
							lan_clube2 = jogo.jog_clube2,
							lan_numero = int(lance_numero),
							lan_minuto = minuto,
							lan_descricao = lance_descricao,
							lan_classe = lance_classe,
							lan_link_sites =lance_link_sites,
							lan_link_videos = lance_link_videos
					)
						
					# tem que se colocar agora, para ter um ID
					lance_obj.put();
					memcache_objs[str(lance_obj.key().id())] = lance_obj
					flash_messages.append(u"%s %s adicionada" % (lance_obj.kind(), lance_obj.__str__().decode("utf-8","replace") ) ) 
					objs_adicionados += 1
						
#					for jel_index in range(number_jels):
	
					jel_checkbox = self.request.get_all(
							prefix+str(index)+"_jel_checkbox")
					jel_jogador_ids = self.request.get_all(
							prefix+str(index)+"_jel_jogador_id")
					jel_jogador_names = self.request.get_all(
							prefix+str(index)+"_jel_jogador")
					jel_papeis = self.request.get_all(
							prefix+str(index)+"_jel_papel")
						
					for idx, jel_this_checkbox in enumerate(jel_checkbox):
							if jel_this_checkbox == "on" :

								jel_jogador = None
								try:
									jel_jogador = Jogador.get_by_id(int(jel_jogador_ids[idx]))
								except:
									if len(jel_jogador_names) > idx:
										jel_jogador = Jogador.gql("where jdg_nome = ", jel_jogador_names[idx])
									
								if jel_jogador:		
									jel_papel = jel_papeis[idx]
									

									jel_obj = JogadorEmLance(
											jel_lance = lance_obj,
											jel_jogador = jel_jogador,
											jel_papel = jel_papel,
									)
									
									jel_obj.put();
	
									# vamos refrescar a última alteração ao jogador. O lan_ultima_alteracao pode esperar
									jel_jogador.jgd_ultima_alteracao = date
									if jel_jogador in objs:
										objs.remove(jel_jogador)
									objs.append(jel_jogador)
									memcache_objs[str(jel_jogador.key().id())] = jel_jogador							
									flash_messages.append(u"%s adicionado." % jel_obj.kind() )
									#, jel_obj.__str__().decode("utf-8","replace") ) ) 
									jels_adicionados += 1
									
					######### adicionar comentadores ao lance
					# ler variáveis de ccl associada a este lance (falta o ccl_lance...)
					for ccl_index in range(number_ccls):
						
						if self.request.get(
							prefix+str(index)+"_ccl"+str(ccl_index)+"_checkbox") == "on":

							ccl_comentador = None
							ccl_comentador_id = self.request.get(
								prefix+str(index)+"_ccl"+str(ccl_index)+"_comentador")

							try:
								ccl_comentador = Comentador.get_by_id(int(ccl_comentador_id))
							except:
								pass
							
							ccl_decisao = int(self.request.get(
								prefix+str(index)+"_ccl"+str(ccl_index)+"_decisao"))
							ccl_descricao = self.request.get(
								prefix+str(index)+"_ccl"+str(ccl_index)+"_descricao")

							if ccl_comentador:
								ccl_obj = ComentadorComentaLance(
									ccl_comentador = ccl_comentador,
									ccl_lance = lance_obj,
									ccl_descricao = ccl_descricao,
									ccl_decisao = ccl_decisao
								)
									
								ccl_obj.put();
								if ccl_comentador in objs:
									objs.remove(ccl_comentador)
								objs.append(ccl_comentador)
								memcache_objs[str(ccl_comentador.key().id())] = ccl_comentador
								flash_messages.append(u"%s %s adicionado" % (ccl_obj.kind(), ccl_obj.__str__().decode("utf-8","replace") ) ) 
								ccls_adicionados += 1

			jogo.jog_clube1.clu_ultima_alteracao = date
			jogo.jog_clube2.clu_ultima_alteracao = date
			jogo.jog_jornada.jor_competicao.cmp_epoca.epo_ultima_alteracao = date
			jogo.jog_jornada.jor_competicao.cmp_ultima_alteracao = date
			jogo.jog_jornada.jor_ultima_alteracao = date

			if jogo.jog_clube1 in objs:
				objs.remove(jogo.jog_clube1)
			objs.append(jogo.jog_clube1)	
			memcache_objs[str(jogo.jog_clube1.key().id())] = jogo.jog_clube1

			if jogo.jog_clube2 in objs:
				objs.remove(jogo.jog_clube2)
			objs.append(jogo.jog_clube2)	
			memcache_objs[str(jogo.jog_clube2.key().id())] = jogo.jog_clube2

			if jogo.jog_jornada.jor_competicao.cmp_epoca in objs:
				objs.remove(jogo.jog_jornada.jor_competicao.cmp_epoca)
			objs.append(jogo.jog_jornada.jor_competicao.cmp_epoca)
			memcache_objs[str(jogo.jog_jornada.jor_competicao.cmp_epoca.key().id())] = jogo.jog_jornada.jor_competicao.cmp_epoca
					
			if jogo.jog_jornada.jor_competicao in objs:
				objs.remove(jogo.jog_jornada.jor_competicao)
			objs.append(jogo.jog_jornada.jor_competicao)
			memcache_objs[str(jogo.jog_jornada.jor_competicao.key().id())] = jogo.jog_jornada.jor_competicao

			if jogo.jog_jornada in objs:
				objs.remove(jogo.jog_jornada)
			objs.append(jogo.jog_jornada)
			memcache_objs[str(jogo.jog_jornada.key().id())] = jogo.jog_jornada

			if jogo.jog_arbitro:
				jogo.jog_arbitro.arb_ultima_alteracao = date
				if jogo.jog_arbitro in objs:
					objs.remove(jogo.jog_arbitro)
				objs.append(jogo.jog_arbitro)
				memcache_objs[str(jogo.jog_arbitro.key().id())] = jogo.jog_arbitro

			if jogo in objs:
				objs.remove(jogo)
			objs.append(jogo)
			memcache_objs[str(jogo.key().id())] = jogo

# os novos, novos elementos já foram adicionados há muito...
# só restam aqueles que precisam de refrescamento

			db.put(objs)
			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total de lances adicionados: %s" % str(objs_adicionados))
			flash_messages.append(u"Total de comentador_comenta_lances adicionados: %s" % str(ccls_adicionados))
			flash_messages.append(u"Total de jogador_em_lances adicionados: %s" % str(jels_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))			
#########
# CLUBE #
#########
		
		elif objname == "clube":

			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return

###########
# JOGADOR #
###########

		elif objname == "jogador": 
			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return


###########
# ARBITRO #
###########

		elif objname == "arbitro":

			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return

##############
# COMENTADOR #
##############
				
		elif objname == "comentador":
			
			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return

#########
# FONTE #
#########
			
		elif objname == "fonte":
			
			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return

#####################
# CLUBE_TEM_JOGADOR #
#####################

		elif objname == "clube_tem_jogador": 

			# PARA CTJs ASSOCIADOS A UM JOGADOR 
			jgd_id = self.request.get('jgd_id')
			jogador_id = None	
			
			if jgd_id: 
				jogador_id = Jogador.get_by_id(int(jgd_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					jogador = None
					clube = None
					
					if jogador_id:
						jogador = jogador_id
					else:
						jogador = Jogador.all().filter("jgd_nome = ", self.request.get(prefix+str(index)+'_jogador')).get()

					if not jogador:
						error = u"Erro: Não encontrei jogador %s!" % self.request.get(prefix+str(index)+'_jogador')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
					
					try:
						clube = Clube.get_by_id(int(self.request.get(prefix+str(index)+'_clube_id')))
					except: 
						error = u"Erro: Não encontrei clube com id %s!" % self.request.get(prefix+str(index)+'_clube_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

					epocas = []
					for epoca_id in self.request.get_all(prefix+str(index)+'_epocas_id'):
						if epoca_id != "":
							epoca = None
							try:
								epoca = Epoca.get_by_id(int(epoca_id))
							except:
								pass
								#epoca = Epoca.all().filter("__key__ in", [db.Key(epoca_nome)]).get()
						
							if epoca:	
								epocas.append(epoca.key()) 
					
					# agora que está tudo sanitanizado, toca a inserir
			
					obj = ClubeTemJogador(
						ctj_clube = clube,
						ctj_jogador = jogador,
						ctj_epocas = epocas,
						ctj_numero = int(self.request.get(prefix+str(index)+'_numero'))
					)

					### PROPAGAR ALTERAÇOES ###
					clube.clu_ultima_alteracao=date
					if clube in objs:
						objs.remove(clube)
					objs.append(clube)
					memcache_objs[str(clube.key().id())] = clube
					
					jogador.jgd_ultima_alteracao=date
					if jogador in objs:
						objs.remove(jogador)
					objs.append(jogador)
					memcache_objs[str(jogador.key().id())] = jogador
					
					objs.append(obj)
					objs_adicionados += 1

			db.put(objs)
			for obj in objs:
				memcache_objs[str(obj.key().id())] = obj
				
				edit_type = None
				if obj.kind() == "ClubeTemJogador":
					edit_type = "adicionado"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return 
							
#########################
# CLUBE_JOGA_COMPETICAO #
#########################
		
		elif objname == "clube_joga_competicao": 
			
			# PARA CTJs ASSOCIADOS A UM JOGADOR 
			cmp_id = self.request.get('cmp_id')
			competicao_id = None	
			
			if cmp_id: 
				competicao_id = Competicao.get_by_id(int(cmp_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					competicao = None
					if competicao_id:
						competicao = competicao_id
					else:
						try:
							competicao = Competicao.get_by_id(int(self.request.get(prefix+str(index)+'_competicao_id')))
						except:
							pass

					if not competicao:
						error = u"Erro: Não encontrei competicao com id %s!" % self.request.get(prefix+str(index)+'_competicao_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
					
					try:
						clube = Clube.get_by_id(int(self.request.get(prefix+str(index)+'_clube_id')))
					except:
						pass
						
					if not clube: 
						error = u"Erro: Não encontrei clube com id %s!" % self.request.get(prefix+str(index)+'_clube_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

						
					classificacao_anterior = 0
					try:
						classificacao_anterior = int(self.request.get(prefix+str(index)+'_classificacao_anterior'))
					except:
						pass
					
					obj = ClubeJogaCompeticao(
						cjc_clube = clube,
						cjc_competicao = competicao,
						cjc_classificacao_anterior = classificacao_anterior
					)
					
					### PROPAGAR ALTERAÇOES ###
					clube.clu_ultima_alteracao=date
					if clube in objs:
						objs.remove(clube)
					objs.append(clube)
					memcache_objs[str(clube.key().id())] = clube
					
					competicao.cmp_ultima_alteracao=date
					if competicao in objs:
						objs.remove(competicao)
					objs.append(competicao)
					memcache_objs[str(competicao.key().id())] = competicao
					
					objs.append(obj)
					objs_adicionados += 1

			db.put(objs)

			for obj in objs:
				memcache_objs[str(obj.key().id())] = obj
				edit_type = None
				if obj.kind() == "ClubeJogaCompeticao":
					edit_type = "adicionado"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return
#####################
# JOGADOR_JOGA_JOGO #
#####################
			
		elif objname == "jogador_joga_jogo": 

			# PARA JJJs ASSOCIADOS A UM JOGO
			jog_id = self.request.get('jog_id')
			jogo_id = None	
			
			if jog_id: 
				jogo_id = Jogo.get_by_id(int(jog_id))

			jogo = None
			if jogo_id:
				jogo = jogo_id
			else:
				# vamos assumir que todos os lances pertencem a um jogo!
				jogo = Jogo.all().filter("jog_nome = ", self.request.get('lan_jogo')).get()

			if not jogo:
				error = u"Erro: Não encontrei jogo %s!" % self.request.get('lan_jogo')
				logging.error(error)
				memcache.set(new_sid, error, namespace="flash")
				self.redirect(add_sid_to_url(referer, new_sid))
				return

			jogo.jog_ultima_alteracao = date
			if jogo in objs:
				objs.remove(jogo)
			objs.append(jogo)
			memcache_objs[str(jogo.key().id())] = jogo
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on": 
					
					jogador = None
					clube = None
					
					try:
						jogador = Jogador.get_by_id(int(self.request.get(prefix+str(index)+'_jogador_id')))
					except:	
						jogador = Jogador.all().filter("jgd_nome = ", self.request.get(prefix+str(index)+'_jogador')).get()

					if not jogador: 
						error = u"Erro: Não encontrei jogador com nome %s ou id %s!" % (self.request.get(prefix+str(index)+'_jogador'),
	self.request.get(prefix+str(index)+'_jogador_id'))					
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

					try:
						clube = Clube.get_by_id(int(self.request.get(prefix+str(index)+'_clube_id')))
					except:
						error = u"Erro: Não encontrei clube com id %s!" % self.request.get(prefix+str(index)+'_clube_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

						
					# tem de ser assim!
					amarelo = None
					if self.request.get(prefix+str(index)+'_amarelo_minuto'):
						amarelo = int(self.request.get(prefix+str(index)+'_amarelo_minuto'))
					duplo_amarelo = None
					if self.request.get(prefix+str(index)+'_duplo_amarelo_minuto'):
						duplo_amarelo = int(self.request.get(prefix+str(index)+'_duplo_amarelo_minuto'))
					vermelho = None
					if self.request.get(prefix+str(index)+'_vermelho_minuto'):
						vermelho = int(self.request.get(prefix+str(index)+'_vermelho_minuto'))
					substituicao_entrada = None
					if self.request.get(prefix+str(index)+'_substituicao_entrada'):
						substituicao_entrada = int(self.request.get(prefix+str(index)+'_substituicao_entrada'))
					substituicao_saida = None
					if self.request.get(prefix+str(index)+'_substituicao_saida'):
						substituicao_saida = int(self.request.get(prefix+str(index)+'_substituicao_saida'))
					posicao = None
					if self.request.get(prefix+str(index)+'_posicao'):
						posicao = self.request.get(prefix+str(index)+'_posicao')
						
					obj = JogadorJogaJogo(
						jjj_jogador = jogador,
						jjj_jogo = jogo,
						jjj_clube = clube,
						jjj_amarelo_minuto = amarelo,
						jjj_duplo_amarelo_minuto = duplo_amarelo,
						jjj_vermelho_minuto = vermelho,
						jjj_substituicao_entrada = substituicao_entrada,
						jjj_substituicao_saida = substituicao_saida,
						jjj_posicao = posicao
					)
							
					list = [] 
					list_tipos = []
					list_tipos_x = self.request.get_all(prefix+str(index)+'_golos_tipos')

					empty = True
					if self.request.get_all(prefix+str(index)+'_golos_minutos'):
						for item in self.request.get_all(prefix+str(index)+'_golos_minutos'):
							if item != u"": 
								empty = False

					if empty:
						obj.jjj_golos_minutos = list
					else:
						for idx, minuto in enumerate(self.request.get_all(prefix+str(index)+'_golos_minutos')):
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
					for link_video in self.request.get_all(prefix+str(index)+'_golos_link_videos'):
						if link_video != "":
							list_link_videos.append(db.Text(link_video))
				
					if list_link_videos:
						obj.jjj_golos_link_videos = list_link_videos

					jogador.jgd_ultima_alteracao = date
					if jogador in objs:
						objs.remove(jogador)
					objs.append(jogador)
					memcache_objs[str(jogador.key().id())] = jogador

					clube.clu_ultima_alteracao = date
					if clube in objs:
						objs.remove(clube)
					objs.append(clube)
					memcache_objs[str(clube.key().id())] = clube
					
					objs.append(obj)
					objs_adicionados += 1

			db.put(objs)

			for obj in objs:
				memcache_objs[str(obj.key().id())] = obj
				edit_type = None
				if obj.kind() == "JogadorJogaJogo":
					edit_type = "adicionado"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return
			
############################
# COMENTADOR_COMENTA_LANCE #
############################			
			
		elif objname == "comentador_comenta_lance": 
	
### estes são controlados pela página do lance. Ou seja, é o lan_id que vem cá.
### não vamos controlar pela página do comentador.

			# PARA CCLs ASSOCIADOS A UM LANCE
			lan_id = self.request.get('lan_id')
			lance_id = None	
			
			if lan_id: 
				lance_id = Lance.get_by_id(int(lan_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					lance = None
					if lance_id:
						lance = lance_id
					else:
						lance = Lance.all().filter("lan_nome = ", self.request.get(prefix+str(index)+'_lance')).get()

					if not lance:
						error = u"Erro: Não encontrei lance %s!" % self.request.get(prefix+str(index)+'_lance')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
					
					comentador = Comentador.get_by_id(int(self.request.get(prefix+str(index)+'_comentador_id')))
					if not comentador: 
						error = u"Erro: Não encontrei comentador com id %s!" % self.request.get(prefix+str(index)+'_comentador_id')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
						
					obj = ComentadorComentaLance(
						ccl_comentador = comentador,
						ccl_lance = lance,
						ccl_descricao = self.request.get(prefix+str(index)+'_descricao'),
						ccl_decisao = int(self.request.get(prefix+str(index)+'_decisao'))
					)
					lance.lan_jogo.jog_ultima_alteracao = date
					if lance.lan_jogo in objs:
						objs.remove(lance.lan_jogo)
					objs.append(lance.lan_jogo)
					memcache_objs[str(lance.lan_jogo.key().id())] = lance.lan_jogo

					lance.lan_ultima_alteracao = date
					if lance in objs:
						objs.remove(lance)
					objs.append(lance)
					memcache_objs[str(lance.key().id())] = lance
					
					objs.append(obj)
					objs_adicionados += 1

			db.put(objs)
			for obj in objs:
				memcache_objs[str(obj.key().id())] = obj
				edit_type = None
				if obj.kind() == "ComentadorComentaLance":
					edit_type = "adicionada"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return
			
####################
# JOGADOR_EM_LANCE #
####################
			
		elif objname == "jogador_em_lance": 

### estes são controlados pela página do lance. Ou seja, é o lan_id que vem cá.
### não vamos controlar pela página do jogador.

			# PARA JELs ASSOCIADOS A UM LANCE
			lan_id = self.request.get('lan_id')
			lance_id = None	
			
			if lan_id: 
				lance_id = Lance.get_by_id(int(lan_id))
	
			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on":

					# FAIL FAST
					lance = None
					jogador = None
					
					if lance_id:
						lance = lance_id
					else:
						lance = Lance.all().filter("lan_nome = ", self.request.get(prefix+str(index)+'_lance')).get()

					if not lance:
						error = u"Erro: Não encontrei lance %s!" % self.request.get(prefix+str(index)+'_lance')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
					
					try:
						jogador = Jogador.get_by_id(int(self.request.get(prefix+str(index)+'_jogador_id')))
					except:
						jogador = Jogador.all().filter("jgd_nome = ", self.request.get(prefix+str(index)+'_jogador')).get()
					
					if not jogador: 
						error = u"Erro: Não encontrei jogador com nome %s!" % self.request.get(prefix+str(index)+'_jogador')
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return

					# agora que está tudo sanitanizado, toca a inserir
					obj = JogadorEmLance(
						jel_jogador = jogador,
						jel_lance = lance,
						jel_papel = self.request.get(prefix+str(index)+'_papel')
					)
					
					jogador.jgd_ultima_alteracao = date
					if jogador in objs:
						objs.remove(jogador)
					objs.append(jogador)
					memcache_objs[str(jogador.key().id())] = jogador

					lance.lan_jogo.jog_ultima_alteracao = date
					if lance.lan_jogo in objs:
						objs.remove(lance.lan_jogo)
					objs.append(lance.lan_jogo)
					memcache_objs[str(lance.lan_jogo.key().id())] = lance.lan_jogo

					lance.lan_ultima_alteracao = date
					if lance in objs:
						objs.remove(lance)
					objs.append(lance)
					memcache_objs[str(lance.key().id())] = lance
					
					objs.append(obj)
					objs_adicionados += 1

			db.put(objs)
			memcache_objs[str(obj.key().id())] = obj
			for obj in objs:
				edit_type = None
				if obj.kind() == "JogadorEmLance":
					edit_type = "adicionada"
				else: 
					edit_type = "refrescada"
				flash_messages.append(u"%s %s: %s" % (obj.kind(), edit_type, obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set_multi(memcache_objs, time=86400)
			flash_messages.append(u"Total edições: %s" %str(objs_adicionados))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return
			
######################
# ACUMULADOR JORNADA #
######################
			
		elif objname == "acumulador_jornada": 

			for index in range(number):
				
				if self.request.get(prefix+str(index)+'_checkbox') == "on": 
					
					jornada = None
			
					jor_nome = self.request.get(prefix+str(index)+"_jornada")
					if jor_nome: 
						jornada = Jornada.all().filter("jor_nome = ", jor_nome).get()
					
					if not jornada:
						error = u"Erro: Não encontrei jornada %s!" % jor_nome 
						logging.error(error)
						memcache.set(new_sid, error, namespace="flash")
						self.redirect(add_sid_to_url(referer, new_sid))
						return
			
					stats = acumulador_jornada.gera(jornada)
			
					versao = None
					try:
						versao = int(self.request.get(prefix+str(index)+'_versao'))
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

					flash_messages.append(u"%s %s: %s" % (obj.kind(), "adicionado", obj.__str__().decode("utf-8","replace") ) ) 

			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return
			
#########################
# ACUMULADOR COMPETICAO #
#########################
			
		elif objname == "acumulador_competicao": 
			
			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return

####################
# ACUMULADOR EPOCA #
####################
			
		elif objname == "acumulador_epoca": 
			
			flash_messages.append(u"Erro: New multiple not avaliable for %s" % (objname))
			memcache.set(new_sid, "<BR>".join(flash_message), namespace="flash")
			self.redirect(add_sid_to_url(referer, new_sid))
			return
