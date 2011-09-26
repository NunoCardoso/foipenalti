# -*- coding: utf-8 -*-

import os
import datetime
import logging
import re
import config 

from classes import *
from detalhe_clube import DetalheClube

class DetalheClubeLances(DetalheClube):
		
	# memcache vars
	cache_namespace = "detalhe_clube_lances"
	render_this_page_without_main = True
	
	def get(self):
		self.decontaminate_vars()
		self.checkCacheFreshen()
		self.requestHandler()
		return 
		
	def renderDados(self):
		
		dados = Lance.all().filter("lan_epoca = ", self.epoca).filter("lan_clubes = ", self.clube.key()).order("lan_data").fetch(1000)

		return dados

	def renderHTML(self):
		
		html = self.render_subdir('clube','detalhe_clube_lances.html', {
			"lances":self.dados,
			"clube":self.clube,
			"epoca":self.epoca,
			"data":datetime.datetime.now()
		})
	
		return html