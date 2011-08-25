import os
from classes import *

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR="templates"

USE_CACHE_DADOS = False
EPOCA_CORRENTE = Epoca.all().filter("epo_nome = ", u"2011/2012").get()
ULTIMA_EPOCA_NA_DB = Epoca.all().filter("epo_nome = ", u"2011/2012").get()
COMPETICAO_CORRENTE = EPOCA_CORRENTE.epo_competicoes.filter("cmp_tipo = ", u"Liga").get()
VERSAO_ACUMULADOR=2
DEVEL = True

def getCurrentHost():
	CURRENT_HOST = None
	if os.environ.has_key("HTTP_HOST"):
		if DEVEL:
			if os.environ["HTTP_HOST"].startswith("localhost"):
				CURRENT_HOST='localhost:8080'
			elif os.environ["HTTP_HOST"].endswith("latest.foipenalti.appspot.com"):
				CURRENT_HOST= os.environ["HTTP_HOST"]
			else:
				CURRENT_HOST = 'www.foipenalti.com'
		else:
			if os.environ["HTTP_HOST"].startswith("localhost"):
				CURRENT_HOST='localhost:8080'

	return CURRENT_HOST
	
# presente em todos os templates
SETTINGS = {
	 'maintitle': "Foi Penalti!",
	 'image_avatar': "http://a2.twimg.com/profile_images/1109160638/avatar_bigger.png",
	
	#### BLOG STUFF 
    'title': 'Blog do \'Foi Penalti!\'',
    'description': "O tira-teimas do sistema",
    'author': 'Nuno Cardoso',
    'email': 'foipenalti@foipenalti.com',
    'url': 'http://www.foipenalti.com',
    'items_per_page': 10,
	 'current_host': getCurrentHost(),
    'google_analytics': False,
    'disqus': "foipenalti"
}
