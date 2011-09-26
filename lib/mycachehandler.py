# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import users 
import logging
import config
import os
import re
import datetime
import hashlib
import django

from classes import *
from myhandler import MyHandler

HTTP_DATE_FMT = "%a, %d %b %Y %H:%M:%S GMT"

class MyCacheHandler(MyHandler):

# classes que estendem isto podem popular estas variáveis, durante a verificação se a cache 
# está fresca ou não, assim poupa-se umas chamadas à memcache e DB

	use_cache = True # use cache or not
	refreshen_cache = False # check if it needs to be refreshen
	render_this_page_without_main = True # True to render the page alone without the main. False to use main as wrapper.
	
	softcache_content_html = None
	softcache_all_html = None
	hardcache_html = None
	cache_namespace = None
	user_is_admin = False
	
	def head(self):
		self.response.set_status(200)
		return
	
	def checkIfAdminUser(self):
		user = users.get_current_user()
		if user:
			self.user_is_admin = users.is_current_user_admin()

	def requestHandler(self):
		
		self.checkIfAdminUser()
		
		if self.use_cache and not self.refreshen_cache:
			
			# hack: if RSS:
			if self.cache_namespace == "rss":
			   self.response.headers['Content-Type'] = 'application/rss+xml'

# 1: check cache HTML
			
			client_etags = None
			
			# cliente tem eTags
			if 'If-None-Match' in self.request.headers:
				client_etags = [x.strip('" ') for x in self.request.headers['If-None-Match'].split(',')]
			
			# 1.1 check SOFTCACHE HTML
			#logging.debug("1.1 check soft cache HTML")
			softcache_content_html = None

			if self.softcache_content_html:
				softcache_content_html = self.softcache_content_html
			else:
				softcache_content_html = memcache.get(self.cache_url, namespace="html")

			if softcache_content_html:
				if softcache_content_html.has_key("signature"):
					
					last_modified = softcache_content_html['date'].strftime(HTTP_DATE_FMT)
					self.response.headers['Last-Modified'] = str(last_modified)
					self.response.headers['ETag'] = '"%s"' % str(softcache_content_html['signature']) # unicode to str

					if client_etags and softcache_content_html['signature'] in client_etags:
						logging.info("Client request with ETag, returning 304 from softcache_html") 
						self.response.set_status(304)
						return
					else:
						logging.info("Client request with NO ETag, returning 200 from softcache_html") 
						if self.render_this_page_without_main:
							softcache_all_html = softcache_content_html["content"]
						else:
							blocks = {"title":softcache_content_html["title"]}
							if self.user_is_admin:
								blocks.update({"admin":softcache_content_html["admin"]})
							
							softcache_all_html = self.render_main_with_blocks(softcache_content_html["content"], blocks)
						
						self.response.out.write(softcache_all_html)
						self.response.set_status(200)
						return
			
			# if not softcache_html...
			
			# 1.2 check HARDCACHE HTML
			#logging.debug("1.2 check hard cache HTML")
			
			this_hardcache_html = None

			if self.hardcache_html:
				this_hardcache_html = self.hardcache_html
			else:
				this_hardcache_html = hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
				
			if this_hardcache_html:
				
				# test IF THERE IS CONTENT, to be a valid HTML cached content
				if this_hardcache_html.cch_signature and this_hardcache_html.cch_content:
					
					# let's refrest SOFTCACHE
					#logging.debug("1/1 Refreshing softcache_html from hardcache_html") 
					memcache.set(self.cache_url, {
						"title": this_hardcache_html.cch_title,
						"admin": this_hardcache_html.get_admin_url(),
						"content": this_hardcache_html.cch_content,
						"date":this_hardcache_html.cch_date,
						"signature":this_hardcache_html.cch_signature
						}, namespace="html", time=86400)
					
					last_modified = this_hardcache_html.cch_date.strftime(HTTP_DATE_FMT)
					self.response.headers['Last-Modified'] = str(last_modified)
					self.response.headers['ETag'] = '"%s"' % str(this_hardcache_html.cch_signature) # unicode to str

					if client_etags and this_hardcache_html.cch_signature in client_etags:
						# set a 304
						logging.info("Client request with ETag, returning 304 from soft_HTML <- hard_HTML") 
						self.response.set_status(304)
						return
					else:
						# set a 200 - may be new user
						logging.info("Client request with NO ETag, returning 200 from soft_HTML <- hard_HTML") 
						if self.render_this_page_without_main:
							hardcache_all_html = this_hardcache_html.cch_content
						else:
							blocks = {"title":this_hardcache_html.cch_title}
							if self.user_is_admin:
								blocks.update({"admin":this_hardcache_html.get_admin_url()})
							
							hardcache_all_html = self.render_main_with_blocks(this_hardcache_html.cch_content, blocks)
						
						self.response.out.write(hardcache_all_html)
						self.response.set_status(200)
						return

# if not softcache_html and not hardcache_html... 

# 2 CHECK CHACHE DADOS
# Aqui já não se aplica ETags... isso é só para HTML

			# 2.1 SOFTCACHE DADOS
			if config.USE_CACHE_DADOS:
			#	logging.debug("2.1 check soft cache DADOS")
				softcache_dados =  memcache.get(self.cache_url, namespace="dados")
				if softcache_dados:
					if softcache_dados.has_key("signature"):
						if client_etags and softcache_dados['signature'] in client_etags:
						# Client has an up-to-date HTML version, but I don't have it in the cache_HTML?  Weird... 
							logging.warning("Client request with ETag, but I don't have nonthing on [soft|hard]cache_html...") 
				
					# either way, let's render a new HTML. We have to return a body on any request...
					self.dados = softcache_dados["dados"]
					self.html = self.renderHTML()
					self.title = self.renderTitle()
					
					signature = hashlib.md5(self.html.encode("ascii","ignore")).hexdigest()
					date = datetime.datetime.now()
						
					# refresh hardcache_html
					#	logging.debug("1/2 Refreshing HARDcache_html from softcache_dados") 
					hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
					if not hardcache_html:
						hardcache_html = CacheHTML(cch_url = self.cache_url)
						
					hardcache_html.cch_namespace = self.cache_namespace
					hardcache_html.cch_signature = signature
					hardcache_html.cch_date = date
					hardcache_html.cch_title = self.title
					hardcache_html.cch_content = self.html if not type(self.html) is django.utils.safestring.SafeUnicode else self.html.encode("utf-8") 
						
					hardcache_html.put()
						
					# refresh softcache_html
					#logging.debug("2/2 Refreshing softcache_html from softcache_dados") 
					memcache.set(self.cache_url, {
						"title": hardcache_html.cch_title,
						"admin": hardcache_html.get_admin_url(),
						"content": hardcache_html.cch_content,
						"date":hardcache_html.cch_cdate,
						"signature":hardcache_html.cch_signature
					}, namespace="html", time=86400)
				
					# return 200
					logging.info("Client request, returning 200 from from soft_HTML <- hard_HTML <- soft_DADOS") 
					last_modified = hardcache_html.cch_cdate.strftime(HTTP_DATE_FMT)
					self.response.headers['Last-Modified'] = str(last_modified)
					self.response.headers['ETag'] = '"%s"' % str(hardcache_html.cch_signature)
					if self.render_this_page_without_main:
						hardcache_all_html = hardcache_html.cch_conten
					else:
						blocks = {"title":hardcache_html.cch_title}
						if self.user_is_admin:
							blocks.update({"admin":hardcache_html.get_admin_url()})
						
						hardcache_all_html = self.render_main_with_blocks(hardcache_html.cch_content, blocks)
					
					self.response.out.write(hardcache_all_html)
					self.response.set_status(200)
					return
				
				#  2.2 check HARDCACHE DADOS
				#logging.debug("2.2 check hard cache DADOS")
				hardcache_dados = CacheDados.all().filter("ccd_url = ",self.cache_url).get()
				if hardcache_dados:

					if hardcache_dados.ccd_signature:
						if client_etags and hardcache_dados.ccd_signature in client_etags:
							# Client has an up-to-date HTML version, but I don't have it in the cache_HTML?  Weird... 
							logging.warning("Client request with ETag, but I don't have nonthing on [soft|hard]cache_html...") 
					
					# either way, let's render a new HTML. We have to return a body on any request...
					self.dados = hardcache_dados.ccd_content
					self.html = self.renderHTML()
					self.title = self.renderTitle()
				
					# let's refrest SOFTCACHE_DADOS
					#logging.debug("1/3 Refreshing softcache_dados from hardcache_dados") 
					memcache.set(self.cache_url, {
						"title": hardcache_dados.ccd_title,
						"admin": hardcache_dados.get_admin_url(),
						"content": hardcache_dados.ccd_content,
						"date":hardcache_dados.ccd_date,
						"signature":hardcache_dados.ccd_signature
						}, namespace="dados", time=86400)
				
					# let's refresh HARDCACHE_HTML
					#logging.debug("2/3 Refreshing hardcache_html from softcache_dados") 


					hardcache_html = CacheHTML.all().filter("cch_url = ", self.cache_url).get()
					if not hardcache_html:
						hardcache_html = CacheHTML(self.cache_url)
						
					hardcache_html.cch_namespace = hardcache_dados.ccd_namespace
					hardcache_html.cch_signature = hardcache_dados.ccd_signature
					hardcache_html.cch_date = hardcache_dados.ccd_date,
					hardcache_html.cch_content = self.html if not type(self.html) is django.utils.safestring.SafeUnicode else self.html.encode("utf-8") 
						
					hardcache_html.put()

					# let's refresh SOFTCACHE_HTML
					#logging.debug("3/3 Refreshing softcache_html from hardcache_html") 
					memcache.set(self.cache_url, {
						"title": hardcache_html.cch_title,
						"admin": hardcache_html.get_admin_url(),
						"content": hardcache_html.cch_content,
						"date":hardcache_html.cch_date,
						"signature":hardcache_html.cch_signature
						}, namespace="html", time=86400)
				
					# let's handle request	
					# set a 200 
					logging.info("Client request, returning 200 from from soft_HTML <- hard_HTML <- soft_DADOS <- hardDADOS") 
					last_modified = hardcache_html.cch_date.strftime(HTTP_DATE_FMT)
					self.response.headers['Last-Modified'] = str(last_modified)
					self.response.headers['ETag'] = '"%s"' % str(hardcache_html.cch_signature)
					if self.render_this_page_without_main:
						hardcache_all_html = hardcache_html.cch_content
					else:
						blocks = {"title":hardcache_html.cch_title}
						if self.user_is_admin:
							blocks.update({"admin":hardcache_html.get_admin_url()})
						
						hardcache_all_html = self.render_main_with_blocks(hardcache_html.cch_content, blocks)
					
					self.response.out.write(hardcache_all_html)
					self.response.set_status(200)
					return
		
# 3. if not cache, or
# if cache, and everything fails (soft_html, hard_html, soft_dados, hard_dados
	
		if not self.use_cache:
			logging.info("FORÇADO a gerar dados e regenerar cache por comando GET") 
		#else:
		#	if self.refreshen_cache:
			#	logging.info("Há cache OBSOLETA, tenho que gerar dados frescos") 
			#else:
			#	logging.info("Não há cache, tenho que gerar dados novo") 
						
			# either way, let's render a new HTML. We have to return a body on any request...
		self.dados = self.renderDados()
		self.html = self.renderHTML()
		self.title = self.renderTitle()

		sig = None

		if not type(self.html) is django.utils.safestring.SafeUnicode:
			sig = self.html.decode("utf-8","ignore")
		else:
			sig = self.html

		signature = hashlib.md5(sig.encode("ascii","ignore")).hexdigest()

		date = datetime.datetime.now()
			
		if config.USE_CACHE_DADOS:
			
		# let's refresh HARDCACHE_DADOS
			# logging.debug("1/4 Refreshing hardcache_dados") 
			hardcache_dados = CacheDados.all().filter("ccd_url = ",self.cache_url).get()
			if not hardcache_dados:			
				hardcache_dados = CacheDados(ccd_url = self.cache_url);
			
			hardcache_dados.ccd_namespace = self.cache_namespace	
			hardcache_dados.ccd_signature = signature
			hardcache_dados.ccd_date = date
			hardcache_dados.ccd_title = self.title
			hardcache_dados.ccd_content = self.dados
			hardcache_dados.put()
				
			# let's refrest SOFTCACHE_DADOS
			#logging.debug("2/4 Refreshing softcache_dados from hardcache_dados") 
			memcache.set(self.cache_url, {
				"title": hardcache_dados.ccd_title,
				"admin": hardcache_dados.get_admin_url(),
				"content": hardcache_dados.ccd_content,
				"date":hardcache_dados.ccd_date,
				"signature":hardcache_dados.ccd_signature
				}, namespace="dados", time=86400)
				
		#logging.info(self.html)
		# let's refresh HARDCACHE_HTML
		#logging.debug("3/4 Refreshing hardcache_html from softcache_dados") 
		hardcache_html = CacheHTML.all().filter("cch_url = ",self.cache_url).get()
		if not hardcache_html:
			hardcache_html = CacheHTML(
			cch_url = self.cache_url)
		
		hardcache_html.cch_namespace = self.cache_namespace	
		hardcache_html.cch_signature = signature
		hardcache_html.cch_date = date
		hardcache_html.cch_content = self.html if not type(self.html) is django.utils.safestring.SafeUnicode else self.html.encode("utf-8") 
		hardcache_html.cch_title = self.title
		hardcache_html.put()

		# let's refresh SOFTCACHE_HTML
		#logging.debug("4/4 Refreshing softcache_html from hardcache_html") 
		memcache.set(self.cache_url, {
			"title": hardcache_html.cch_title,
			"admin": hardcache_html.get_admin_url(),
			"content": hardcache_html.cch_content,
			"date":hardcache_html.cch_date,
			"signature":hardcache_html.cch_signature
			}, namespace="html", time=86400)
		
		# let's handle request	
		# set a 200 
		logging.info("Client request, returning 200 from from soft_HTML <- hard_HTML <- soft_DADOS <- hardDADOS <- GENERATE") 
		last_modified = hardcache_html.cch_date.strftime(HTTP_DATE_FMT)
		self.response.headers['Last-Modified'] = str(last_modified)
		self.response.headers['ETag'] = '"%s"' % str(hardcache_html.cch_signature)
		if self.render_this_page_without_main:
			hardcache_all_html = hardcache_html.cch_content
		else:
			blocks = {"title":hardcache_html.cch_title}
			if self.user_is_admin:
				blocks.update({"admin":hardcache_html.get_admin_url()})
			
			hardcache_all_html = self.render_main_with_blocks(hardcache_html.cch_content, blocks)
		self.response.out.write(hardcache_all_html)
		self.response.set_status(200)
		return