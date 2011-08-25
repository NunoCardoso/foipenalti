# -*- coding: utf-8 -*-

from google.appengine.api import memcache

import os
import datetime
import logging
import re
import config 
import mymemcache

from classes import *

# epoca
# competicao
# jogador[]
# clube[]


def get_lista_clubes():
		
		lista_todos_clubes = None
#		logging.info("getting")
		cacheresultados = memcache.get('lista_todos_clubes')
		cache_old = mymemcache.check(cacheresultados, ['clube'])
			
		if not cacheresultados: # or cache_old:
			lista_todos_clubes = []
#			logging.info("generating")
			clubes = Clube.all().order("clu_nome_curto")
			for clube in clubes:
				lista_todos_clubes.append(clube)
			
			memcache.set('lista_todos_clubes',
				{"date":datetime.datetime.today(),
				'lista_todos_clubes':lista_todos_clubes}
			)
		else:
#			logging.info(cacheresultados)
			lista_todos_clubes  = cacheresultados['lista_todos_clubes']
		return lista_todos_clubes
		


def get_lista_todos_clubes_por_visitas():
		
		lista_todos_clubes = None
		cacheresultados = memcache.get('lista_todos_clubes_por_visitas')
		cache_old = mymemcache.check(cacheresultados, ['clube'])
			
		if not cacheresultados or cache_old:
			lista_todos_clubes = []
			clubes = Clube.all().order("-clu_num_visitas")
			for clube in clubes:
				lista_todos_clubes.append(clube)
			
			memcache.set('lista_todos_clubes_por_visita',
				{"date":datetime.datetime.today(),
				'lista_todos_clubes_por_visita':lista_todos_clubes}
			)
		else:
			lista_todos_clubes  = cacheresultados['lista_todos_clubes_por_visita']
		return lista_todos_clubes


def get_lista_epocas():
		
		ultima_epoca_na_db = config.ULTIMA_EPOCA_NA_DB
		lista_epocas = []
		cacheresultados = memcache.get('lista_todos_epocas')
		cache_old = mymemcache.check(cacheresultados, ['epoca'])
			
		if not cacheresultados or cache_old:
			epocas = Epoca.all()
			for epoca in epocas:
		#		if epoca.epo_data_inicio >= ultima_epoca_na_db.epo_data_inicio:
					lista_epocas.append(epoca)
			# True is for a reverse
			lista_epocas = sorted(lista_epocas, cmp=lambda x,y: cmp(x.epo_nome, y.epo_nome))
			lista_epocas.reverse()	
			memcache.set('lista_todos_epocas',{"date":datetime.datetime.today(),
				'lista_todos_epocas':lista_epocas},time=86400)
		else:
			lista_epocas = cacheresultados['lista_todos_epocas']
		return lista_epocas

		
def get_lista_arbitros():
		lista_arbitros = []
		cacheresultados = memcache.get('lista_todos_arbitros')
		cache_old = mymemcache.check(cacheresultados, ['arbitro'])
		
		if not cacheresultados or cache_old:
			arbitros = Arbitro.all()
			for arbitro in arbitros:
				lista_arbitros.append(arbitro)
			lista_arbitros = sorted(lista_arbitros, cmp=lambda x,y: cmp(x.arb_nome, y.arb_nome))
			memcache.set('lista_todos_arbitros',{"date":datetime.datetime.today(),
				'lista_todos_arbitros':lista_arbitros},time=86400)
		else:
			lista_arbitros = cacheresultados['lista_todos_arbitros']
		return lista_arbitros

	
def get_lista_competicoes_por_visitas():
		lista_competicoes = []
		cacheresultados = memcache.get('lista_todas_competicoes')
		cache_old = mymemcache.check(cacheresultados, ['competicao'])
			
		if not cacheresultados or cache_old:
			competicoes = Competicao.all().order("-cmp_numero_visitas")
			for competicao in competicoes:
				lista_competicoes.append(competicao)
			memcache.set('lista_todas_competicoes',{"date":datetime.datetime.today(),
				'lista_todas_competicoes':lista_competicoes},time=86400)
		else:
			lista_competicoes = cacheresultados['lista_todas_competicoes']
		return lista_competicoes

	
def get_lista_competicoes():
		lista_competicoes = []
		cacheresultados = memcache.get('lista_todas_competicoes')
		cache_old = mymemcache.check(cacheresultados, ['competicao'])
			
		if not cacheresultados or cache_old:
			competicoes = Competicao.all()
			for competicao in competicoes:
				lista_competicoes.append(competicao)
			lista_competicoes = sorted(lista_competicoes, cmp=lambda x,y: cmp(x.cmp_nome, y.cmp_nome))
			memcache.set('lista_todas_competicoes',{"date":datetime.datetime.today(),
				'lista_todas_competicoes':lista_competicoes},time=86400)
		else:
			lista_competicoes = cacheresultados['lista_todas_competicoes']
		return lista_competicoes


def get_lista_comentadores():
		lista_comentadores = []
		cacheresultados = memcache.get('lista_todos_comentadores')
		cache_old = mymemcache.check(cacheresultados, ['comentador'])
			
		if not cacheresultados or cache_old:
			comentadores = Comentador.all()
			for comentador in comentadores:
				lista_comentadores.append(comentador)
			lista_comentadores = sorted(lista_comentadores, cmp=lambda x,y: cmp(x.com_nome, y.com_nome))
			memcache.set('lista_todos_comentadores',{"date":datetime.datetime.today(),
				'lista_todos_comentadores':lista_comentadores},time=86400)
		else:
			lista_comentadores = cacheresultados['lista_todos_comentadores']
		return lista_comentadores


def get_lista_competicoes_tipos():
		lista_competicoes_tipos = []
		cacheresultados = memcache.get('lista_todas_competicoes_tipos')
		cache_old = mymemcache.check(cacheresultados, ['competicao'])
			
		if not cacheresultados or cache_old:
			competicoes = Competicao.all()
			for competicao in competicoes:
				if not competicao.cmp_tipo in lista_competicoes_tipos:
					# pode ter lista de competições de várias épocas, o que importa é que 
					# venha com um tipo de competição diferente
					lista_competicoes_tipos.append(competicao)
			lista_competicoes_tipo = sorted(lista_competicoes_tipos, cmp=lambda x,y: cmp(x.cmp_tipo, y.cmp_tipo))
			memcache.set('lista_todas_competicoes_tipos',{"date":datetime.datetime.today(),
				'lista_todos_competicoes_tipos':lista_competicoes_tipo},time=86400)
		else:
			lista_competicoes_tipos = cacheresultados['lista_todos_competicoes_tipos']
		return lista_competicoes_tipos


def get_lista_tipos_lances():
		lista_tipos_lances = []
		cacheresultados = memcache.get('lista_todos_tipos_lances')
		if cacheresultados: 
			return cacheresultados['lista_todos_tipos_lances']
			
		if not cacheresultados:
			
			# devolve uma lista com tuplos
			#lista = sorted(Lance.translation_tipo.copy().items(), key=lambda t: t[0])
#			logging.info(lista)
			lista = Lance.translation_classe
			# devolve um dicionário de lances bem ordenadinha; OrderedDict lembra-se das posições!
			memcache.set('lista_todos_tipos_lances',{"date":datetime.datetime.today(),
				'lista_todos_tipos_lances':lista},time=86400)
			return lista
			
def get_lista_tipos_jels():
		lista_tipos_jels = []
		cacheresultados = memcache.get('lista_todos_tipos_jels')
		if cacheresultados: 
			return cacheresultados['lista_todos_tipos_jels']
			
		if not cacheresultados:
			
			# devolve uma lista com tuplos
			lista = sorted(JogadorEmLance.translation.copy().items(), key=lambda t: t[1])
			memcache.set('lista_todos_tipos_jels',{"date":datetime.datetime.today(),
				'lista_todos_tipos_jels':lista},time=86400)
			return lista

def get_lista_posicoes():
		lista_posicoes = []
		cacheresultados = memcache.get('lista_posicoes')
		if cacheresultados: 
			return cacheresultados['lista_posicoes']
			
		if not cacheresultados:
			
			# devolve uma lista com tuplos
			lista = sorted(Jogador.translation_posicao.copy().items(), key=lambda t: t[0])
			memcache.set('lista_posicoes',{"date":datetime.datetime.today(),
				'lista_posicoes':lista},time=86400)
			return lista

def get_lista_tacticas():
		lista_tacticas = []
		cacheresultados = memcache.get('lista_todas_tacticas')
		if cacheresultados: 
			return cacheresultados['lista_todas_tacticas']
			
		if not cacheresultados:
			
			# devolve uma lista com tuplos
			lista = Jogo.tacticas
			memcache.set('lista_todas_tacticas',{"date":datetime.datetime.today(),
				'lista_todas_tacticas':lista},time=86400)
			return lista



def get_top_jogadores_populares():
		return Jogador.all().order("-jgd_numero_visitas").fetch(10)


def get_top_clubes_populares():
	return Clube.all().order("-clu_numero_visitas").fetch(10)


def get_top_jogos_populares():
		return Jogo.all().order("-jog_numero_visitas").fetch(10)


def get_top_arbitros_populares():
		return Arbitro.all().order("-arb_numero_visitas").fetch(10)


def get_top_lances_populares():
		return Lance.all().order("-lan_numero_visitas").fetch(10)


def get_top_jornadas_recentes():
		return Jornada.all().order("-jor_ultima_alteracao").fetch(10)


def get_top_jogadores_recentes():
		return Jogador.all().order("-jgd_ultima_alteracao").fetch(10)


def get_top_jogos_recentes():
		return Jogo.all().order("-jog_ultima_alteracao").fetch(10)


def get_top_arbitros_recentes():
		return Arbitro.all().order("-arb_ultima_alteracao").fetch(10)


def get_top_lances_recentes():
	return Lance.all().order("-lan_ultima_alteracao").fetch(10)
