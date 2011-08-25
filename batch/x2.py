# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
epoca = Epoca.all().filter("epo_nome = ", "2011/2012").get()
competicao = Competicao.all().filter("cmp_nome = ", "2011/2012:Liga").get()

data = datetime.datetime.strptime("2011-08-24", "%Y-%m-%d") 
		
# Jornadas
j = Jornada(
	jor_numero_visitas = 0,
	jor_ultima_alteracao = date,
	jor_nome = competicao.cmp_nome+":1",
	jor_data = data.date(),
	jor_epoca = competicao.cmp_epoca,
	jor_competicao = competicao,
	jor_nome_curto = "1ª Jornada",
	jor_nome_completo = self.request.get('jor_nome_completo'),
	jor_ordem = int(self.request.get('jor_ordem')),
	jor_link_zz = db.Link(self.request.get('jor_link_zz'))
)	


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
