# -*- coding: utf-8 -*-
import os
# os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# from google.appengine.dist import use_library
# use_library('django', '1.2')

import config
import datetime
import sys
import logging
import re

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# Django selection

# brom blog: Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'externals'))
sys.path.insert(2, os.path.join(config.APP_ROOT_DIR, 'handlers'))
sys.path.insert(3, os.path.join(config.APP_ROOT_DIR, 'lib'))
sys.path.insert(4, os.path.join(config.APP_ROOT_DIR, 'tags'))
sys.path.insert(5, os.path.join(config.APP_ROOT_DIR, 'tests'))

# main template tag handlers for django
import wsgiref.handlers
template.register_template_library('tags.templatetags')
template.register_template_library('tags.set_var')

from lib.myhandler import MyHandler
from lib import autocomplete
from admin import delete, edit, list, new, new_multiple, save, save_multiple, admin, home
from tasks import acumulador_task_manager, refresh_acumuladores, parse_jogo
from mail import sendmail

# handler
import blog, blogadmin
# clube
from clube import detalhe_clube, detalhe_clube_jogadores, detalhe_clube_jogos, detalhe_clube_lances
from clube import detalhe_clube_indices, detalhe_clube_arbitros, detalhe_clube_sumario
# jogador
from jogador import detalhe_jogador, detalhe_jogador_jogos, detalhe_jogador_lances
from jogador import detalhe_jogador_arbitros, detalhe_jogador_sumario
# arbitro
from arbitro import detalhe_arbitro, detalhe_arbitro_jogos, detalhe_arbitro_lances
from arbitro import detalhe_arbitro_clubes, detalhe_arbitro_jogadores, detalhe_arbitro_sumario
# competicao
from competicao import detalhe_competicao, detalhe_competicao_clubes
from competicao import detalhe_competicao_sumario, detalhe_competicao_indices
from competicao import detalhe_competicao_arbitros, detalhe_competicao_jogos, detalhe_competicao_jogadores
# epoca
from epoca import detalhe_epoca, detalhe_epoca_sumario, detalhe_epoca_arbitros, detalhe_epoca_clubes
from epoca import detalhe_epoca_jogadores, detalhe_epoca_indices, detalhe_epoca_jogos

import detalhe_jogo, detalhe_lance, detalhe_jornada, homepage
#procurar
import procurar_arbitro, procurar_jogador, procurar_jogo, procurar_lance
import procurar_epoca, procurar_competicao, procurar_clube, resultado

class Contactos(MyHandler):
	def get(self):
		self.render_to_output('contactos.html', {})
		
class Agradecimentos(MyHandler):
	def get(self):
		self.render_to_output('agradecimentos.html', {})

class Termos(MyHandler):
	def get(self):
		self.render_to_output('termos.html', {})
	
class Faq(MyHandler):
	def get(self):
		self.render_to_output('faq.html', {})		

class Regulamentos(MyHandler):
	def get(self):
		self.render_to_output('regulamentos.html', {})		

class Duvidas(MyHandler):
	def get(self):
		self.render_to_output('duvidas.html', {})		

class Error404Handler(MyHandler):
	def get(self):
		self.response.set_status(404)
		self.render_to_output('error.html', {})		

class Redirect(MyHandler):
	def get(self):
		if self.request.path == "/top_jogos":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_jogos")		
		elif self.request.path == "/top_arbitros":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_arbitros")		
		elif self.request.path == "/top_clubes":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_clubes")		
		elif self.request.path == "/top_jogadores":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_jogadores")		
		elif self.request.path == "/icc":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_indices")		
		elif self.request.path == "/classificacao":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_sumario")		
		elif self.request.path == "/tabela_icc":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_tabela_icc")		

### 5
		elif self.request.path == "/ica":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_ica")		
		elif self.request.path == "/tabela_resultados":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_tabela_resultados")		
		elif self.request.path == "/top_lances":
			self.redirect("/detalhe_competicao?menu=detalhe_competicao_lances")		

def main():
  application = webapp.WSGIApplication([

			# admin
			(r'/admin/?', admin.Admin),
			(r'/admin/([^/]*)/delete', delete.Delete),
			(r'/admin/([^/]*)/new', new.New),
			(r'/admin/([^/]*)/new_multiple', new_multiple.NewMultiple),
			(r'/admin/([^/]*)/edit', edit.Edit),
			(r'/admin/([^/]*)/save', save.Save),
			(r'/admin/([^/]*)/save_multiple', save_multiple.SaveMultiple),
			(r'/admin/([^/]*)/list', list.List),
			(r'/admin/([^/]*)', home.RedirectHome),
			(r'/admin/([^/]*)/', home.Home),
			(r'/admin/clear-cache', blogadmin.ClearCacheHandler),
			(r'/admin/post/create', blogadmin.CreatePostHandler),
			(r'/admin/post/edit/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', blogadmin.EditPostHandler),

			# homepage
			(r'/',homepage.HomePage),
			
			# stuff
			(r'/faq',Faq),
			(r'/duvidas',Duvidas),
			(r'/regulamentos',Regulamentos),
			(r'/termos',Termos),
			(r'/agradecimentos',Agradecimentos),
			(r'/contactos',Contactos),
			
			# search
			(r'/procurar_epoca', procurar_epoca.ProcurarEpoca),
			(r'/procurar_clube', procurar_clube.ProcurarClube),
			(r'/procurar_competicao', procurar_competicao.ProcurarCompeticao),
			(r'/procurar_arbitro', procurar_arbitro.ProcurarArbitro),
			(r'/procurar_jogador', procurar_jogador.ProcurarJogador),
			(r'/procurar_jogo', procurar_jogo.ProcurarJogo),
			(r'/procurar_lance', procurar_lance.ProcurarLance),
			(r'/resultado',resultado.Resultado),
			
			# detalhes
			(r'/detalhe_jornada', detalhe_jornada.DetalheJornada),
			(r'/detalhe_jogo', detalhe_jogo.DetalheJogo),
			(r'/detalhe_lance', detalhe_lance.DetalheLance),

			(r'/detalhe_clube', detalhe_clube.DetalheClube),
			(r'/detalhe_clube_jogadores', detalhe_clube_jogadores.DetalheClubeJogadores),
			(r'/detalhe_clube_arbitros', detalhe_clube_arbitros.DetalheClubeArbitros),
			(r'/detalhe_clube_sumario', detalhe_clube_sumario.DetalheClubeSumario),
			(r'/detalhe_clube_lances', detalhe_clube_lances.DetalheClubeLances),
			(r'/detalhe_clube_indices', detalhe_clube_indices.DetalheClubeIndices),
			(r'/detalhe_clube_jogos', detalhe_clube_jogos.DetalheClubeJogos),

			(r'/detalhe_epoca', detalhe_epoca.DetalheEpoca),
			(r'/detalhe_epoca_jogos', detalhe_epoca_jogos.DetalheEpocaJogos),
			(r'/detalhe_epoca_clubes', detalhe_epoca_clubes.DetalheEpocaClubes),
			(r'/detalhe_epoca_sumario', detalhe_epoca_sumario.DetalheEpocaSumario),
			(r'/detalhe_epoca_indices', detalhe_epoca_indices.DetalheEpocaIndices),
			(r'/detalhe_epoca_jogadores', detalhe_epoca_jogadores.DetalheEpocaJogadores),
			(r'/detalhe_epoca_arbitros', detalhe_epoca_arbitros.DetalheEpocaArbitros),

			(r'/detalhe_competicao', detalhe_competicao.DetalheCompeticao),
			(r'/detalhe_competicao_clubes', detalhe_competicao_clubes.DetalheCompeticaoClubes),
			(r'/detalhe_competicao_jogos', detalhe_competicao_jogos.DetalheCompeticaoJogos),
			(r'/detalhe_competicao_sumario', detalhe_competicao_sumario.DetalheCompeticaoSumario),
			(r'/detalhe_competicao_indices', detalhe_competicao_indices.DetalheCompeticaoIndices),
			(r'/detalhe_competicao_jogadores', detalhe_competicao_jogadores.DetalheCompeticaoJogadores),
			(r'/detalhe_competicao_arbitros', detalhe_competicao_arbitros.DetalheCompeticaoArbitros),

			(r'/detalhe_jogador', detalhe_jogador.DetalheJogador),
			(r'/detalhe_jogador_jogos', detalhe_jogador_jogos.DetalheJogadorJogos),
			(r'/detalhe_jogador_lances', detalhe_jogador_lances.DetalheJogadorLances),
			(r'/detalhe_jogador_arbitros', detalhe_jogador_arbitros.DetalheJogadorArbitros),
			(r'/detalhe_jogador_sumario', detalhe_jogador_sumario.DetalheJogadorSumario),

			(r'/detalhe_arbitro', detalhe_arbitro.DetalheArbitro),
			(r'/detalhe_arbitro_jogos', detalhe_arbitro_jogos.DetalheArbitroJogos),
			(r'/detalhe_arbitro_lances', detalhe_arbitro_lances.DetalheArbitroLances),
			(r'/detalhe_arbitro_clubes', detalhe_arbitro_clubes.DetalheArbitroClubes),
			(r'/detalhe_arbitro_jogadores', detalhe_arbitro_jogadores.DetalheArbitroJogadores),
			(r'/detalhe_arbitro_sumario', detalhe_arbitro_sumario.DetalheArbitroSumario),

# fast redirects
			(r'/top_jogos', Redirect),
			(r'/top_arbitros', Redirect),
			(r'/top_clubes', Redirect),
			(r'/top_jogadores', Redirect),
			(r'/top_lances', Redirect),
			(r'/classificacao', Redirect),
			(r'/icc', Redirect),
			(r'/ica', Redirect),
			(r'/tabela_icc', Redirect),
			(r'/tabela_resultados', Redirect),
			(r'/mail/sendmail', sendmail.SendMail),

# autocompletes
			(r'/autocomplete/nome_jogador', autocomplete.NomeJogador),
			(r'/autocomplete/nome_clube', autocomplete.NomeClube),
			(r'/autocomplete/nome_arbitro', autocomplete.NomeArbitro),
			(r'/autocomplete/competicoes', autocomplete.CompeticoesDeEpoca),

# tasks
			(r'/task/acumulador_task_manager', acumulador_task_manager.AcumuladorTaskManager),
			(r'/task/refresh/([^/]*)', refresh_acumuladores.Refresh),
			(r'/task/parse_jogo', parse_jogo.ParseJogo),

#blog
			(r'/blog', blog.IndexHandler),
			(r'/blog/', blog.IndexHandler),
			(r'/blog/rss2', blog.RSS2Handler),
			(r'/blog/tag/([-\w]+)', blog.TagHandler),
			(r'/blog/(\d{4})', blog.YearHandler),
			(r'/blog/(\d{4})/(\d{2})', blog.MonthHandler),
			(r'/blog/(\d{4})/(\d{2})/(\d{2})', blog.DayHandler),
			(r'/blog/(\d{4})/(\d{2})/(\d{2})/([-\w]+)', blog.PostHandler),

# 404
			('/.*', Error404Handler)
			], debug=False)
			
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()
