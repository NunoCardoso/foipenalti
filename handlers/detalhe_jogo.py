# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from lib.mycachehandler import MyCacheHandler
from google.appengine.api import memcache
from lib.detalhe_icc import DetalheICC

class DetalheJogo(MyCacheHandler):
		
	# memcache vars
	cache_namespace = "detalhe_jogo"
	cache_url = None

	#memcache values
	dados = None
	html = None
	sid = None

	# get vars
	jogo = None
	
	referer = None
	
	def get(self):
		self.decontaminate_vars()
		if not self.jogo:
			error = u"Erro: Não há jogo com id %s" % jog_id
			logging.error(error)
			new_sid = self.generate_sid()
			memcache.set(str(new_sid), error, namespace="flash")
			self.add_sid_to_cookie(new_sid)
			self.redirect(referer)	
			return
			
		self.checkCacheFreshen()
		self.requestHandler()
		self.jogo.jog_numero_visitas += 1
		self.jogo.put() 
		return 
		
	def checkCacheFreshen(self):
		data_cache = None # data do HRML gerado em cache
		
		self.softcache_html =  memcache.get(self.cache_url, namespace=self.cache_namespace)
		if self.softcache_html:
			data_cache = self.softcache_html['date']
		else:
			self.hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
			if self.hardcache_html:
				data_cache = self.hardcache_html.cch_date
		
		if data_cache and self.jogo.jog_ultima_alteracao > data_cache:
			self.refreshen_cache = True
			logging.info("refreshen cache = true")
			
	def renderDados(self):
		
		jogo_dados = {
			"guarda_redes1":None,
			"guarda_redes2":None,
			"jogadores_inicio1":[], 
			"jogadores_subst1":[],
			"jogadores_inicio2":[],
			"jogadores_subst2":[],
			"lances":[],
			"golos_virtuais_clube1":0,
			"golos_virtuais_clube2":0,
			"icc_clube1":0,
			"icc_clube2":0,
			"ia":""
		}

# setas de navegação

		jornada_anterior = self.jogo.jog_jornada.jor_competicao.cmp_jornadas.filter("jor_ordem = ", self.jogo.jog_jornada.jor_ordem - 1).get()
		jornada_posterior = self.jogo.jog_jornada.jor_competicao.cmp_jornadas.filter("jor_ordem = ", self.jogo.jog_jornada.jor_ordem + 1).get()
		jogo_anterior_clube1 = None
		jogo_anterior_clube2 = None
		jogo_posterior_clube1 = None
		jogo_posterior_clube2 = None
		
		if jornada_anterior:
			jogo_anterior_clube1 = jornada_anterior.jor_jogos.filter("jog_clubes = ", self.jogo.jog_clube1).get()
			jogo_anterior_clube2 = jornada_anterior.jor_jogos.filter("jog_clubes = ", self.jogo.jog_clube2).get()
		if jornada_posterior:
			jogo_posterior_clube1 = jornada_posterior.jor_jogos.filter("jog_clubes = ", self.jogo.jog_clube1).get()
			jogo_posterior_clube2 = jornada_posterior.jor_jogos.filter("jog_clubes = ", self.jogo.jog_clube2).get()

# jjjs

		for jjj_jogador in self.jogo.jog_jogadores:
			jogador = jjj_jogador.jjj_jogador
			clube = jjj_jogador.jjj_clube
			ctj = ClubeTemJogador.all().filter("ctj_jogador = ", jogador).filter("ctj_clube = ", clube).filter("ctj_epocas = ", self.jogo.jog_epoca.key()).get()
			numero = None
			try:
				numero = ctj.ctj_numero
			except:
				numero = 0
			props = {
			"jogador":jogador,
			"numero": numero,	
			"golos": len(jjj_jogador.jjj_golos_minutos),
			"golos_videos": jjj_jogador.jjj_golos_link_videos,
			"golos_minutos": jjj_jogador.jjj_golos_minutos,
			"golos_tipos": jjj_jogador.jjj_golos_tipos,
			"amarelo": jjj_jogador.jjj_amarelo_minuto,
			"duplo_amarelo": jjj_jogador.jjj_duplo_amarelo_minuto,
			"vermelho": jjj_jogador.jjj_vermelho_minuto,
			"entrada": jjj_jogador.jjj_substituicao_entrada,
			"saida": jjj_jogador.jjj_substituicao_saida
			}
					
			if clube.key() == self.jogo.jog_clube1.key():
				if props['entrada']:
					jogo_dados['jogadores_subst1'].append(props)
				else:
					if "Guarda-Redes" in jogador.jgd_posicao or "GR" in jogador.jgd_posicao :
						jogo_dados['guarda_redes1'] = props
					else:
						jogo_dados['jogadores_inicio1'].append(props)

			else:
				if props['entrada']:
					jogo_dados['jogadores_subst2'].append(props)
				else:
					if "Guarda-Redes" in jogador.jgd_posicao or "GR" in jogador.jgd_posicao :
						jogo_dados['guarda_redes2'] = props
					else:
						jogo_dados['jogadores_inicio2'].append(props)
			
		# vamos ordenar os jogadores por número na camisola
		jogo_dados['jogadores_inicio1'] = sorted(jogo_dados['jogadores_inicio1'], 
			cmp=lambda x,y: cmp(x['numero'], y['numero']))
		jogo_dados['jogadores_inicio2'] = sorted(jogo_dados['jogadores_inicio2'], 
			cmp=lambda x,y: cmp(x['numero'], y['numero']))
		jogo_dados['jogadores_subst1'] = sorted(jogo_dados['jogadores_subst1'], 
			cmp=lambda x,y: cmp(x['numero'], y['numero']))
		jogo_dados['jogadores_subst2'] = sorted(jogo_dados['jogadores_subst2'], 
			cmp=lambda x,y: cmp(x['numero'], y['numero']))
			
		icc_clube1 = 0.0			
		icc_clube2 = 0.0
				
		jogo_dados["golos_virtuais_clube1"] = self.jogo.jog_golos_virtuais_clube1
		jogo_dados["golos_virtuais_clube2"] = self.jogo.jog_golos_virtuais_clube2
		if not self.jogo.jog_clube_beneficiado and not self.jogo.jog_clube_prejudicado:
			jogo_dados["icc_clube1"] = self.jogo.jog_icc
			jogo_dados["icc_clube2"] = self.jogo.jog_icc
		if  self.jogo.jog_clube_beneficiado and self.jogo.jog_clube_beneficiado.key() == self.jogo.jog_clube1.key():
			jogo_dados["icc_clube1"] = self.jogo.jog_icc
			jogo_dados["icc_clube2"] = -1 * self.jogo.jog_icc
		if  self.jogo.jog_clube_beneficiado and self.jogo.jog_clube_beneficiado.key() == self.jogo.jog_clube2.key():
			jogo_dados["icc_clube1"] = -1 * self.jogo.jog_icc
			jogo_dados["icc_clube2"] = self.jogo.jog_icc

		jogo_dados["ia"] = self.jogo.jog_influencia_arbitro
		lances = []
		
# vamos adicionar lances
		for lance in self.jogo.jog_lances.order("lan_numero"):
			prop = {"lance": lance, "comentarios":lance.lan_comentadores.fetch(1000),
		 	"protagonistas": lance.lan_jogadores.fetch(1000),
		 	"tipo": Lance.translation_classe[lance.lan_classe]
			}
			lances.append(prop)
			
# vamos adicionar detalhe icc
		lista_lances = self.jogo.jog_lances.fetch(1000)

# acumulador_jornadas, como folte dos lances
		acu_jornadas = {}
		acumuladores = AcumuladorJornada.all().filter("acuj_jornada = ", self.jogo.jog_jornada).filter("acuj_versao = ", config.VERSAO_ACUMULADOR)
		for acu in acumuladores:
			acu_jornadas[acu.acuj_jornada.jor_nome] = acu.acuj_content

		detalhe_icc = DetalheICC()
		detalhe_icc.setLances(lista_lances)
		detalhe_icc.setAcumuladoresJornadas(acu_jornadas)
		resultados = detalhe_icc.gera()

		detalhe_icc_jogos = resultados["jogos"]

		return {
		"jogos":jogo_dados,
		"lances":lances,
		
		"jornada_anterior":jornada_anterior,
		"jornada_posterior":jornada_posterior,
		"jogo_anterior_clube1":jogo_anterior_clube1,
		"jogo_anterior_clube2":jogo_anterior_clube2,
		"jogo_posterior_clube1":jogo_posterior_clube1,
		"jogo_posterior_clube2":jogo_posterior_clube2,
		
		"detalhe_icc_jogos":detalhe_icc_jogos
		}

	def renderHTML(self):
		flash_message = None
		if self.sid is not None:
			flash_message = memcache.get(str(self.sid), namespace="flash")
			if flash_message:
				memcache.delete(str(self.sid), namespace="flash")
	
		ficha_de_jogo_html = self.render_subdir("gera","gera_ficha_de_jogo.html", {
			"jogo": self.jogo,
			"jogo_dados": self.dados["jogos"]
		})
			
		sumario_actuacao_arbitro_html = self.render_subdir("gera","gera_sumario_actuacao_arbitro.html", {
			"jogo": self.jogo,
			"jogo_dados": self.dados["jogos"]
		})
		
		lances_html = []
		for lance in self.dados["lances"]: 
			lances_html.append(self.render_subdir("gera","gera_lance.html", {
			"lance":lance
			}))
			
		html = self.render('detalhe_jogo.html', {
			"jogo": self.jogo,
			"jogo_dados": self.dados["jogos"],
			
			"jornada_anterior":self.dados["jornada_anterior"],
			"jornada_posterior":self.dados["jornada_posterior"],
			"jogo_anterior_clube1":self.dados["jogo_anterior_clube1"],
			"jogo_anterior_clube2":self.dados["jogo_anterior_clube2"],
			"jogo_posterior_clube1":self.dados["jogo_posterior_clube1"],
			"jogo_posterior_clube2":self.dados["jogo_posterior_clube2"],
			
			"detalhe_icc_jogos":self.dados["detalhe_icc_jogos"],
			
			"lances_html":lances_html,
			"ficha_de_jogo_html":ficha_de_jogo_html,
			"sumario_actuacao_arbitro_html":sumario_actuacao_arbitro_html,
			"flash":flash_message
		})
		
		return html
		
	def decontaminate_vars(self):
		
 		jog_id = None
		jogo = None
		values = None

		if os.environ.has_key("HTTP_REFERER"):
			self.referer = os.environ['HTTP_REFERER']
		else:
			self.referer = "/procurar_jogo"
		
		if self.request.get("cache") and self.request.get("cache") == "false":
			self.use_cache = False

		self.sid =self.get_sid_from_cookie()

		try:
			jog_id = int(self.request.get("id"))
			jogo = Jogo.get_by_id(jog_id) 
		except:
			if self.request.get("jogo"):
				try:
					jogo = Jogo.all().filter("jog_nome = ", self.request.get("jogo")).get()
				except:
					pass
		
		if jogo:
			self.jogo = jogo
		
			self.cache_url = self.request.path+"?id="+str(jogo.key().id())
