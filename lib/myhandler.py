# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
import logging
import config
import os
import re
import datetime
import traceback
import urllib
import Cookie
import time
import listas

from exception import BadParameterException
from google.appengine.api import datastore
from google.appengine.runtime.apiproxy_errors import *
from google.appengine.api.datastore_errors import *
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext.db import Timeout

# myHandler gere mensagens de erro, e também gere formas de geração de página.

class MyHandler(webapp.RequestHandler):

##################
#### RENDER ######
##################

	pattern = re.compile("<!--STARTCUTTINGPART-->(.*)<!--ENDCUTTINGPART-->", re.S)
	
	def render_template_block(self, template_file, template_values={}):
		#renderer = Renderer()
		val = MyHandler.render(self, template_file, template_values)
		m = MyHandler.pattern.search(val)
		return m.group(1)

	def render_subdir_template_block(self, template_dir, template_file, template_values={}):
		#renderer = Renderer()
		val = MyHandler.render_subdir(self, template_dir, template_file, template_values)
		m = MyHandler.pattern.search(val)
		return m.group(1)
		
	def render(self, template_file, template_values={}):
		"""Render a template"""
		
		values = {
		'host':os.environ['HTTP_HOST'],
		'request':self.request,
		'settings': config.SETTINGS,
		"goback": os.environ['HTTP_REFERER'] if os.environ.has_key('HTTP_REFERER') else "javascript:history.back()",
		"lista_top_jogadores_populares": listas.get_top_jogadores_populares(),
		"lista_top_jogos_populares": listas.get_top_jogos_populares(),
		"lista_top_arbitros_populares": listas.get_top_arbitros_populares(),
		"lista_top_lances_populares": listas.get_top_lances_populares()
		}
		values.update(template_values)

		template_path = os.path.join(config.APP_ROOT_DIR, config.TEMPLATE_DIR, template_file)
		return template.render(template_path, values)

	def render_subdir(self, template_dir, template_file, template_values={}):
		"""Render a template"""
		values = {
		'host':os.environ['HTTP_HOST'],
		'request':self.request,
		'settings': config.SETTINGS,
		"goback": os.environ['HTTP_REFERER'] if os.environ.has_key('HTTP_REFERER') else "javascript:history.back()",
		"lista_top_jogadores_populares": listas.get_top_jogadores_populares(),
		"lista_top_jogos_populares": listas.get_top_jogos_populares(),
		"lista_top_arbitros_populares": listas.get_top_arbitros_populares(),
		"lista_top_lances_populares": listas.get_top_lances_populares()
		}
		 
		values.update(template_values)

		template_path = os.path.join(config.APP_ROOT_DIR, config.TEMPLATE_DIR, template_dir, template_file)
		
		return template.render(template_path, values)
	
	def render_to_output(self, template_file, template_values={}):
	#	renderer = Renderer()
		val = MyHandler.render(self, template_file, template_values)
		self.response.out.write(val)
		
	def render_subdir_to_output(self, template_dir, template_file, template_values={}):
	#	renderer = Renderer()
		val = MyHandler.render_subdir(self, template_dir, template_file, template_values)
		self.response.out.write(val)

	# et milliseconds	
	def generate_sid(self):
		return int(round(time.time() * 1000))

	# add sid to cookie
	def add_sid_to_cookie(self, sid):
		expiration = datetime.datetime.now() + datetime.timedelta(minutes=1)
		self.response.headers.add_header('Set-Cookie','sid='+str(sid)+'; expires='+expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")+'; path=/;')
			
	def get_sid_from_cookie(self):
		return self.request.cookies.get("sid") 

####################
### EXCEPÇÕES ######
####################
	
	def handle_exception(self, exception, debug_mode):

		pagina_anterior = os.environ['HTTP_REFERER'] if os.environ.has_key('HTTP_REFERER') else self.request.url
		
#		para páginas admin, colocar erro no flash
		if self.request.path.startswith("/admin/"):
			new_sid = self.generate_sid()
			trace = "".join(traceback.format_exc())
			memcache.set(str(new_sid), "Erro:" + trace, namespace="flash")
			logging.error(trace)
			self.add_sid_to_cookie(new_sid)
			return self.redirect(pagina_anterior)
			
		# para páginas públicas, mostrar erro.		
		renderPage = None
		
			
		exception_error = u"<H3>Lamentamos, mas o seu pedido não pode ser satisfeito. :(</H3><P>A página que pediu gerou uma excepção. Pedimos desculpa pelo sucedido.</P><P>Como tal, peço-lhe o favor de <a href='mailto:foipenalti@foipenalti.com?subject=Erro%%20no%%20Foi%%20penalti&body=%s'>reportar o erro a mim, para que eu possa reparar o programa o mais depressa possível</A>.</P><P>Obrigado pela atenção. Entretanto, pode <A HREF='%s'>voltar à página anterior</A> e optar por outra ligação enquanto o problema não for resolvido.</P>" 
		
		timeout_error = "<H3>Lamentamos, mas o servidor está ocupado. :(</H3><P>Os servidores estão  sobrecarregados, e o seu pedido não foi satisfeito a tempo. Por favor, <a href='%s'>volte a tentar daqui a alguns minutos</A>. Obrigado pela compreensão.</P>"

		deadline_error = "<H3>Lamentamos, mas o pedido demorou muito tempo. :(</H3><P>O seu pedido não foi satisfeito a tempo (30 segundos), por isso tive que desistir. Por favor, <a href='%s'>volte a tentar daqui a alguns minutos</A>. Obrigado pela compreensão.</P>"
		
		quota_error = "<H3>Irra, vocês são mais que as mães!</H3><P>Lamentamos, mas a quota de largura de banda está esgotada. Isto só volta a zero no próximo dia. Sou muito forreta para pagar ao Google mais quota de largura de banda...portanto, volte cá amanhã. Desculpe.</P>"
		
		index_error = "<H3>Lamentamos, mas o servidor está em manutenção. :(</H3><P>Os servidores estão ocupados a gerar índices para as pesquisas, e como tal infelizmente não podemos satisfazer o seu pedidos. Por favor, <a href='%s'>volte a tentar daqui a alguns minutos</A>. Obrigado pela compreensão.</P>"
		trace = None
		
		if debug_mode:
			super(MyHandler, self).handle_exception(exception, debug_mode)
		else:
			trace = "".join(traceback.format_exc())
			logging.error(trace)
			logging.error("Tipo de excepção:")
			logging.error(type(exception))
			
			if isinstance(exception, Timeout):
        # Display a timeout-specific error page
				errorpage = self.render('exception.html', {
				 "erro": timeout_error % self.request.url
				})
				
			elif isinstance(exception, BadParameterException):
				errorpage = self.render('exception.html', {
				 "erro": exception.error (trace, pagina_anterior)
				})

			elif isinstance(exception, DeadlineExceededError):
				errorpage = self.render('exception.html', {
				 "erro": deadline_error % self.request.url
				})
			
			elif isinstance(exception, NeedIndexError):
					errorpage = self.render('exception.html', {
					 "erro": index_error % self.request.url
					})
			elif isinstance(exception, OverQuotaError):
 					errorpage = self.render('exception.html', {
					 "erro": quota_error 
					})
			else:
        		# Display a generic 500 error page.
				errorpage = self.render('exception.html', {
				 "erro": exception_error % (trace, pagina_anterior)
				})
				
			self.response.clear()
			self.response.set_status(500)
			self.response.out.write(errorpage)


