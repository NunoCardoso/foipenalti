# -*- coding: utf-8 -*-

from google.appengine.api import memcache
from google.appengine.ext import db
import logging
import pickle
import sys
import os

# from blog: Force sys.path to have our own directory first, so we can import from it.
app_root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0,app_root_dir)
sys.path.insert(1, os.path.join(app_root_dir, 'externals'))
sys.path.insert(2, os.path.join(app_root_dir, 'handlers'))
sys.path.insert(3, os.path.join(app_root_dir, 'lib'))

from externals import markdown

# http://stackoverflow.com/questions/1953784/can-i-store-a-python-dictionary-in-googles-bigtable-datastore-without-serializin
class DictProperty(db.Property):
  data_type = dict

  def get_value_for_datastore(self, model_instance):
    value = super(DictProperty, self).get_value_for_datastore(model_instance)
    return db.Blob(pickle.dumps(value))

  def make_value_from_datastore(self, value):
    if value is None:
      return dict()
    return pickle.loads(value)

  def default_value(self):
    if self.default is None:
      return dict()
    else:
      return super(DictProperty, self).default_value().copy()

  def validate(self, value):
    if not isinstance(value, dict):
      raise db.BadValueError('Property %s needs to be convertible '
                             'to a dict instance (%s) of class dict' % (self.name, value))
    return super(DictProperty, self).validate(value)

  def empty(self, value):
    return value is None

###########
## EPOCA ##
###########

class Epoca(db.Model): 

	epo_numero_visitas = db.IntegerProperty() 
	epo_ultima_alteracao = db.DateTimeProperty() 
	epo_nome = db.StringProperty() 
	epo_data_inicio = db.DateProperty()
	epo_data_fim = db.DateProperty()

	fields = [{'Nº visitas':'epo_numero_visitas'},
				{'Última alteração':'epo_ultima_alteracao'},
				{'Nome':'epo_nome'},
				{'Data início':'epo_data_inicio'},
				{'Data fim':'epo_data_fim'}]

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.epo_nome == other.epo_nome
		return False
			
	def __str__( self ):
		return self.epo_nome.encode( "utf-8" )

################
## COMPETICAO ##
################

class Competicao(db.Model):

	cmp_numero_visitas = db.IntegerProperty() 
	cmp_ultima_alteracao = db.DateTimeProperty() 
	cmp_nome = db.StringProperty() # formato epo_nome:cmp_tipo
	cmp_nome_completo = db.StringProperty() # nome usado
	cmp_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_competicoes')
	cmp_tipo = db.StringProperty() 
	cmp_link_foto = db.StringProperty() 
	cmp_link_zz = db.LinkProperty() 

	cmp_lugares_descida =  db.ListProperty(int) #[15, 16]
	cmp_lugares_liga_campeoes =  db.ListProperty(int) #[1]
	cmp_lugares_eliminatorias_liga_campeoes = db.ListProperty(int) #[2]
	cmp_lugares_liga_europa  =  db.ListProperty(int) #[3, 4, 5]
	cmp_numero_jornadas = db.IntegerProperty()
	
	fields = [{'Nº visitas':'cmp_numero_visitas'},
				{'Última alteração':'cmp_ultima_alteracao'},
				{'Nome':'cmp_nome'},
				{'Nome completo':'cmp_nome_completo'},
				{'Época':'cmp_epoca'},
				{'Tipo':'cmp_tipo'},
				{'Foto':'cmp_link_foto'},
				{'Nº de jornadas':'cmp_numero_jornadas'},
				{'Lugares de descida':'cmp_lugares_descida'},
				{'Lugares de Liga dos Campeões':'cmp_lugares_liga_campeoes'},
				{'Lugares de eliminatórias da Liga dos Campeões':'cmp_lugares_eliminatorias_liga_campeoes'},
				{'Lugares da Liga Europa':'cmp_lugares_liga_europa'},
				{'Link':'cmp_link_zz'}]	

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.cmp_nome == other.cmp_nome
		return False

	def __str__( self ):
		return self.cmp_nome.encode( "utf-8" )

#############
## JORNADA ##
#############

class Jornada(db.Model): 
	
	jor_numero_visitas = db.IntegerProperty() 
	jor_ultima_alteracao = db.DateTimeProperty() 
	jor_nome = db.StringProperty() # epo_nome:cmp_tipo:jor_nome_curto
	jor_data = db.DateProperty() 
	jor_nome_curto = db.StringProperty() # 6, Taca2, 2F3J
	jor_nome_completo = db.StringProperty() # 6a jornada, Meia final, 2ª fase, 3ª jornada
	jor_ordem = db.IntegerProperty()
	jor_competicao = db.ReferenceProperty(Competicao,
	 	required=True,
      collection_name='cmp_jornadas')
	jor_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_jornadas')
	jor_link_zz = db.LinkProperty() 

	fields = [{'Nº visitas':'jor_numero_visitas'},
				{'Última alteração':'jor_ultima_alteracao'},
				{'Nome':'jor_nome'},
				 {'Data':'jor_data'},
				 {'Época':'jor_epoca'},
				 {'Competição':'jor_competicao'},
				 {'Nome curto':'jor_nome_curto'},
				 {'Nome completo':'jor_nome_completo'},
				 {'Ordem':'jor_ordem'},
				 {'Link':'jor_link_zz'}]

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.jor_nome == other.jor_nome
		return False
				
	def __str__( self ):
		return self.jor_nome.encode( "utf-8" )


###########
## CLUBE ##
###########

class Clube(db.Model): 

	clu_numero_visitas = db.IntegerProperty() 
	clu_ultima_alteracao = db.DateTimeProperty() 
	clu_nome_completo = db.StringProperty() 
	clu_nome_curto = db.StringProperty() 
	clu_nome = db.StringProperty() 
	clu_link_logo = db.StringProperty() 
	clu_link_zz = db.LinkProperty() 

	fields = [{'Nº visitas':'clu_numero_visitas'},
			    {'Última alteração':'clu_ultima_alteracao'},
			    {'Nome':'clu_nome'},
				 {'Nome completo':'clu_nome_completo'},
			    {'Nome curto':'clu_nome_curto'},
				 {'Emblema':'clu_link_logo'},
				 {'Link':'clu_link_zz'}]

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.clu_nome == other.clu_nome
		return False
				
	def __str__( self ):
		return self.clu_nome.encode( "utf-8" )

#############
## JOGADOR ##
#############

class Jogador(db.Model): 

	jgd_numero_visitas = db.IntegerProperty() 
	jgd_ultima_alteracao = db.DateTimeProperty() 
	jgd_nome = db.StringProperty()
	jgd_nome_completo = db.StringProperty()
	jgd_numero = db.IntegerProperty() 
	jgd_link_foto = db.StringProperty() 
	jgd_link_zz = db.LinkProperty() 
	jgd_posicao = db.StringListProperty()
	jgd_clube_actual = db.ReferenceProperty(Clube,
	 	required=True,
      collection_name='jgd_clube_actual')

	translation_posicao = {'GR':'Guarda-Redes','D':'Defesa',
		'DE':'Defesa Esquerdo', 'DC':'Defesa Central', 
		'DD':'Defesa Direito','L':'Líbero','T':'Trinco',
		'MA':'Médio Ala','M':'Médio','MC':'Médio Centro',
		'MD':'Médio Defensivo','MO':'Médio Ofensivo',
		'LD':'Lateral Direito','LE':'Lateral Esquerdo',
		'MAD':'Médio Ala Direito','MAE':'Médio Ala Esquerdo',
		'A':'Avançado','AC':'Avançado Centro',
		'EE':'Extremo Esquerdo','ED':'Extremo Direito',
		'PL':'Ponta-de-Lança'}
	
	fields = [{'Nº visitas':'jgd_numero_visitas'},
			    {'Última alteração':'jgd_ultima_alteracao'},
				 {'Nome':'jgd_nome'},
				 {'Nome completo':'jgd_nome_completo'},
				 {'Número de camisola':'jgd_numero'},
				 {'Posição':'jgd_posicao'},
				 {'Clube actual':'jgd_clube_actual'},
				 {'Foto':'jgd_link_foto'},
				 {'Link':'jgd_link_zz'}
				]
				
	def __str__( self ):
		return self.jgd_nome.encode( "utf-8" )
		
	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.jgd_nome == other.jgd_nome
		return False

#############
## ARBITRO ##
#############

class Arbitro(db.Model): 

	arb_numero_visitas = db.IntegerProperty() 
	arb_ultima_alteracao = db.DateTimeProperty() 
	arb_nome = db.StringProperty() 
	arb_link_foto = db.StringProperty() 
	arb_link_zz = db.LinkProperty() 

	fields = [{'Nº visitas':'arb_numero_visitas'},
				{'Última alteração':'arb_ultima_alteracao'},
				{'Nome':'arb_nome'},
				{'Foto':'arb_link_foto'},
				{'Link':'arb_link_zz'}]

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.arb_nome == other.arb_nome
		return False

	def __str__( self ):
		return self.arb_nome.encode( "utf-8" )

##########
## JOGO ##
##########

class Jogo(db.Model): 
	
	jog_numero_visitas = db.IntegerProperty() 
	jog_ultima_alteracao = db.DateTimeProperty()

	jog_nome = db.StringProperty()
	jog_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_jogos')
	jog_competicao = db.ReferenceProperty(Competicao,
	 	required=True,
      collection_name='cmp_jogos')
	jog_jornada = db.ReferenceProperty(Jornada,
	 	required=True,
      collection_name='jor_jogos')

	jog_data = db.DateTimeProperty()
	jog_clube1 = db.ReferenceProperty(Clube,
		required=True,
      collection_name='clu_jogos_casa')
	jog_clube2 = db.ReferenceProperty(Clube,
		required=True,
      collection_name='clu_jogos_fora')
	jog_golos_clube1 =  db.IntegerProperty()
	jog_golos_clube2 =  db.IntegerProperty()
# não pode ser required=True... posso adicionar jogos sem ter árbitros
	jog_arbitro = db.ReferenceProperty(Arbitro,
      collection_name='arb_jogos')
	jog_tactica_clube1 =  db.StringProperty()
	jog_tactica_clube2 =  db.StringProperty()
	jog_link_sites = db.ListProperty(db.Link)
	jog_link_videos = db.ListProperty(db.Text)
	jog_comentario = db.TextProperty()


## GERADOS AUTOMATICAMENTE ##

	jog_clubes = db.ListProperty(db.Key)
	jog_clube_beneficiado = db.ReferenceProperty(Clube,
      collection_name='clu_jogos_beneficiados')
	jog_clube_prejudicado = db.ReferenceProperty(Clube,
      collection_name='clu_jogos_prejudicados')

	jog_golos_virtuais_clube1 =  db.IntegerProperty()
	jog_golos_virtuais_clube2 =  db.IntegerProperty()

	jog_icc = db.FloatProperty()
	jog_ica = db.FloatProperty()
	jog_influencia_arbitro = db.IntegerProperty()
	jog_julgamento_arbitro = db.IntegerProperty()
	
	tacticas = ["4-5-1","4-4-2","4-3-3","4-2-4",
					"4-2-3-1","4-1-4-1","4-1-3-2",
					"3-4-3","3-5-2"]
					
	fields = [{'Nº visitas':'jog_numero_visitas'},
				{'Última alteração':'jog_ultima_alteracao'},
				{'Nome':'jog_nome'},
				{'Epoca':'jog_epoca'},
				{'Competicao':'jog_competicao'},
				{'Jornada':'jog_jornada'},
				{'Data':'jog_data'},
				{'Clube da casa':'jog_clube1'},
				{'Clube visitante':'jog_clube2'},
				{'Táctica casa':'jog_tactica_clube1'},
				{'Táctica visitante':'jog_tactica_clube2'},
				{'Clubes':'jog_clubes'},
				{'Árbitro':'jog_arbitro'},
				{'Golos da casa':'jog_golos_clube1'},
				{'Golos visitante':'jog_golos_clube2'},
				{'Golos virtuais da casa':'jog_golos_virtuais_clube1'},
				{'Golos virtuais visitante':'jog_golos_virtuais_clube2'},
				{'ICC':'jog_icc'},
				{'ICA':'jog_ica'},
				{'IA':'jog_influencia_arbitro'},
				{'Julgamento árbitro':'jog_julgamento_arbitro'},
				{'Clube beneficiado':'jog_clube_beneficiado'},
				{'Clube prejudicado':'jog_clube_prejudicaado'},
				{'Links sites':'jog_link_sites'},
				{'Links vídeos':'jog_link_videos'},
				{'Comentário':'jog_comentario'}
				]	
	translation_influencia_arbitro = ['--',"O árbitro não teve influência no resultado.",
	"O árbitro teve influência no resultado mas não nos pontos.",
	"O árbitro teve influência no resultado e nos pontos.",
	"Sem informação."]

	translation_julgamento_arbitro = ['--','Sem benefícios','Beneficiou a equipa da casa','Beneficiou a equipa visitante','Sem informação']

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			# pode haver jogos iguais, tipo entre equipas "a definir"
			return self.key().id() == other.key().id()
		return False

	def __str__( self ):
		return self.jog_nome.encode( "utf-8" )
	
	def printjogo(self, clube=None):
		golos1 = ""
		if  self.jog_golos_clube1 != None:
			golos1 = self.jog_golos_clube1
		golos2 = ""
		if  self.jog_golos_clube2 != None:
			golos2 = self.jog_golos_clube2
		
		clube1 = None
		if clube and self.jog_clube1.key().id() == clube:
			clube1 = "<B>%s</B>" % self.jog_clube1.clu_nome_curto	
		else:
			clube1 = self.jog_clube1.clu_nome_curto

		clube2 = None
		if clube and self.jog_clube2.key().id() == clube:
			clube2 = "<B>%s</B>" % self.jog_clube2.clu_nome_curto	
		else:
			clube2 = self.jog_clube2.clu_nome_curto

		return "%s %s - %s %s" % (clube1, golos1, golos2, clube2)
		
class Lance(db.Model):
	
	lan_numero_visitas = db.IntegerProperty() 
	lan_ultima_alteracao = db.DateTimeProperty() 
	lan_nome = db.StringProperty()
	lan_data = db.DateTimeProperty()
	lan_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_lances')
	lan_competicao = db.ReferenceProperty(Competicao,
	 	required=True,
      collection_name='cmp_lances')
	lan_jornada = db.ReferenceProperty(Jornada,
	 	required=True,
      collection_name='jor_lances')
	lan_jogo = db.ReferenceProperty(Jogo,
	 	required=True,
      collection_name='jog_lances')
	lan_clube1 = db.ReferenceProperty(Clube,
		collection_name="clu_casa_lances")
	lan_clube2 = db.ReferenceProperty(Clube,
		collection_name="clu_fora_lances")

	lan_arbitro = db.ReferenceProperty(Arbitro,
		collection_name="arb_lances")
	lan_numero = db.IntegerProperty() # pode haver mais que um lance no mesmo minuto
	lan_minuto =  db.IntegerProperty() 
	lan_descricao = db.TextProperty() #TextProperty pode ser maior que 500, e não é indexada.
	lan_classe = db.IntegerProperty(default=0)
	lan_link_sites = db.ListProperty(db.Link)
	lan_link_videos = db.ListProperty(db.Text)
	lan_comentario = db.TextProperty()

## PREENCHIDOS AUTOMATICAMENTE ##
	lan_clubes = db.ListProperty(db.Key)
	lan_causa = db.IntegerProperty(default=0) 
	lan_apitado = db.IntegerProperty(default=0) 
	lan_consequencia = db.IntegerProperty(default=0)
	# 0 - ?, 1 - benefício casa, 2 - Benefício visitante, 3 - Sem informação	
	lan_julgamento_arbitro = db.IntegerProperty(default=0)
	lan_clube_beneficiado = db.ReferenceProperty(Clube,
      collection_name='clu_lances_beneficiados')
	lan_clube_prejudicado = db.ReferenceProperty(Clube,
      collection_name='clu_lances_prejudicados')

	translation_causa = ['--','golo','penalti','fora-de-jogo','cartão amarelo','cartão vermelho','agressão','livre dentro da área','livre fora da área','jogo perigoso']
	translation_apitado = ['--','assinalado','não assinalado','validado','não validado','mostrado','não mostrado']
	translation_consequencia = ['--','convertido','não convertido','de golo fácil','de golo difícil']
	translation_julgamento_arbitro = ['--','Sem benefícios','Beneficiou a equipa da casa','Beneficiou a equipa visitante','Sem informação']
	
	translation_classe = ['--',
			'Amarelo mostrado a jogador da equipa da casa', 
			'Amarelo mostrado a jogador da equipa visitante', 
			'Amarelo não mostrado a jogador da equipa da casa', 
			'Amarelo não mostrado a jogador da equipa visitante', 

			'Vermelho mostrado a jogador da equipa da casa', 
			'Vermelho mostrado a jogador da equipa visitante', 
			'Vermelho não mostrado a jogador da equipa da casa', 
			'Vermelho não mostrado a jogador da equipa visitante', 

			'Falta perigosa assinalada e convertida, no ataque da equipa da casa', 
			'Falta perigosa assinalada e não convertida, no ataque da equipa da casa', 
			'Falta perigosa assinalada e convertida, no ataque da equipa visitante', 
			'Falta perigosa assinalada e não convertida, no ataque da equipa visitante', 
			'Falta perigosa não assinalada, no ataque da equipa da casa', 
			'Falta perigosa não assinalada, no ataque da equipa visitante', 

			'Fora de jogo assinalado no ataque da equipa da casa, de golo fácil',
			'Fora de jogo assinalado no ataque da equipa da casa, de golo difícil',
			'Fora de jogo assinalado no ataque da equipa visitante, de golo fácil',
			'Fora de jogo assinalado no ataque da equipa visitante, de golo difícil',
			'Fora de jogo não assinalado no ataque da equipa da casa, que resultou em golo', 
			'Fora de jogo não assinalado no ataque da equipa da casa, que não resultou em golo', 
			'Fora de jogo não assinalado no ataque da equipa visitante, que resultou em golo', 
			'Fora de jogo não assinalado no ataque da equipa visitante, que não resultou em golo', 

			'Penalti assinalado e convertido a atacante da equipa da casa', 
			'Penalti assinalado e não convertido a atacante da equipa da casa', 
			'Penalti assinalado e convertido a atacante da equipa visitante', 
			'Penalti assinalado e não convertido a atacante da equipa visitante', 
			'Penalti não assinalado a atacante da equipa da casa', 
			'Penalti não assinalado a atacante da equipa visitante', 

			'Golo marcado e validado para a equipa da casa', 
			'Golo marcado e validado para a equipa visitante', 
			'Golo marcado mas invalidado para a equipa da casa', 
			'Golo marcado mas invalidado para a equipa visitante'
	]

	fields = [{'Nº visitas':'lan_numero_visitas'},
				{'Última alteração':'lan_ultima_alteracao'},
				{'Nome':'lan_nome'},
				{'Época':'lan_epoca'},
				{'Competição':'lan_competicao'},
				{'Jornada':'lan_jornada'},
				{'Jogo':'lan_jogo'},
				{'Data':'lan_data'},
				{'Clube1':'lan_clube1'},
				{'Clube2':'lan_clube2'},
				{'Árbitro':'lan_arbitro'},
				{'Número':'lan_numero'},
				{'Minuto':'lan_minuto'},
				{'Descrição':'lan_descricao'},
				{'Classe':'lan_classe'},
				{'Causa':'lan_causa'},
				{'Apitado':'lan_apitado'},
				{'Consequência':'lan_consequencia'},
				{'Julgamento':'lan_julgamento'},
				{'Clube beneficiado':'lan_clube_beneficiado'},
				{'Clube prejudicado':'lan_clube_prejudicado'},
				{'Links sites':'lan_link_sites'},
				{'Links vídeos':'lan_link_videos'},
				{'Comentário':'lan_comentario'}
				]			

	def decide_lance(self):
		num_decisao = {}
		decisao = None
			
		for comentarios in self.lan_comentadores: 
			if comentarios.ccl_decisao is not None:
				
				decisao_parcial = comentarios.ccl_decisao
				if decisao_parcial == self.translation_julgamento_arbitro.index('Sem informação'):
					decisao_parcial = self.translation_julgamento_arbitro.index('Sem benefícios')
			
				if num_decisao.has_key(decisao_parcial):
					num_decisao[decisao_parcial] += 1
				else:
					num_decisao[decisao_parcial] = 1
			
		# ordenar e obter o que está no topo
		sort = sorted(num_decisao, cmp=lambda x,y: cmp(num_decisao[x], num_decisao[y]), reverse = True)
		if sort:
			decisao = sort[0]
		else:
			decisao = self.translation_julgamento_arbitro.index('Sem benefícios')
		return decisao
	
	def divide_tipo_lance(self):
		lan_causa = 0
		lan_apitado = 0
		lan_consequencia = 0
		
		if self.lan_classe == Lance.translation_classe.index('Amarelo mostrado a jogador da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Amarelo mostrado a jogador da equipa visitante'):
			lan_causa = self.translation_causa.index("cartão amarelo")
			lan_apitado = self.translation_apitado.index("mostrado")
			lan_consequencia = self.translation_consequencia.index("--")
			
		elif self.lan_classe == Lance.translation_classe.index('Vermelho mostrado a jogador da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Vermelho mostrado a jogador da equipa visitante'):
			lan_causa = self.translation_causa.index("cartão vermelho")
			lan_apitado = self.translation_apitado.index("mostrado")
			lan_consequencia = self.translation_consequencia.index("--")
			
		elif self.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e convertida, no ataque da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e convertida, no ataque da equipa visitante'):
			lan_causa = self.translation_causa.index("livre fora da área")
			lan_apitado = self.translation_apitado.index("assinalado")
			lan_consequencia = self.translation_consequencia.index("convertido")
			
		elif self.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e não convertida, no ataque da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Falta perigosa assinalada e não convertida, no ataque da equipa visitante'): 
			lan_causa = self.translation_causa.index("livre fora da área")
			lan_apitado = self.translation_apitado.index("assinalado")
			lan_consequencia = self.translation_consequencia.index("não convertido")
			
		elif self.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa da casa, de golo fácil') or \
			self.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa visitante, de golo fácil'):
			lan_causa = self.translation_causa.index("fora-de-jogo")
			lan_apitado = self.translation_apitado.index("assinalado")
			lan_consequencia = self.translation_consequencia.index("de golo fácil")
			
		elif self.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa da casa, de golo difícil') or \
			self.lan_classe == Lance.translation_classe.index('Fora de jogo assinalado no ataque da equipa visitante, de golo difícil'):
			lan_causa = self.translation_causa.index("fora-de-jogo")
			lan_apitado = self.translation_apitado.index("assinalado")
			lan_consequencia = self.translation_consequencia.index("de golo difícil")
			
		elif self.lan_classe == Lance.translation_classe.index('Penalti assinalado e convertido a atacante da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Penalti assinalado e convertido a atacante da equipa visitante'): 
			lan_causa = self.translation_causa.index("penalti")
			lan_apitado = self.translation_apitado.index("assinalado")
			lan_consequencia = self.translation_consequencia.index("convertido")
			
		elif self.lan_classe == Lance.translation_classe.index('Penalti assinalado e não convertido a atacante da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Penalti assinalado e não convertido a atacante da equipa visitante'): 
			lan_causa = self.translation_causa.index("penalti")
			lan_apitado = self.translation_apitado.index("assinalado")
			lan_consequencia = self.translation_consequencia.index("não convertido")
			
		elif self.lan_classe == Lance.translation_classe.index('Golo marcado e validado para a equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Golo marcado e validado para a equipa visitante'): 
			lan_causa = self.translation_causa.index("golo")
			lan_apitado = self.translation_apitado.index("validado")
			lan_consequencia = self.translation_consequencia.index("--")
			
		elif self.lan_classe == Lance.translation_classe.index('Amarelo não mostrado a jogador da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Amarelo não mostrado a jogador da equipa visitante'):
			lan_causa = self.translation_causa.index("cartão amarelo")
			lan_apitado = self.translation_apitado.index("não mostrado")
			lan_consequencia = self.translation_consequencia.index("--")
			
		elif self.lan_classe == Lance.translation_classe.index('Vermelho não mostrado a jogador da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Vermelho não mostrado a jogador da equipa visitante'):
			lan_causa = self.translation_causa.index("cartão vermelho")
			lan_apitado = self.translation_apitado.index("não mostrado")
			lan_consequencia = self.translation_consequencia.index("--")
			
		elif self.lan_classe == Lance.translation_classe.index('Falta perigosa não assinalada, no ataque da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Falta perigosa não assinalada, no ataque da equipa visitante'):
			lan_causa = self.translation_causa.index("livre fora da área")
			lan_apitado = self.translation_apitado.index("não assinalado")
			
		elif self.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa da casa, que resultou em golo') or \
			self.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa visitante, que resultou em golo'):
			lan_causa = self.translation_causa.index("fora-de-jogo")
			lan_apitado = self.translation_apitado.index("não assinalado")
			lan_consequencia = self.translation_consequencia.index("convertido")
			
		elif self.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa da casa, que não resultou em golo') or \
			self.lan_classe == Lance.translation_classe.index('Fora de jogo não assinalado no ataque da equipa visitante, que não resultou em golo'):
			lan_causa = self.translation_causa.index("fora-de-jogo")
			lan_apitado = self.translation_apitado.index("não assinalado")
			lan_consequencia = self.translation_consequencia.index("não convertido")
			
		elif self.lan_classe == Lance.translation_classe.index('Penalti não assinalado a atacante da equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Penalti não assinalado a atacante da equipa visitante'): 
			lan_causa = self.translation_causa.index("penalti")
			lan_apitado = self.translation_apitado.index("não assinalado")
			
		elif self.lan_classe == Lance.translation_classe.index('Golo marcado mas invalidado para a equipa da casa') or \
			self.lan_classe == Lance.translation_classe.index('Golo marcado mas invalidado para a equipa visitante'): 
			lan_causa = self.translation_causa.index("golo")
			lan_apitado = self.translation_apitado.index("não validado")

		return lan_causa, lan_apitado, lan_consequencia

	def printlance(self):
		golos1 = ""
		if  self.lan_jogo.jog_golos_clube1 != None:
			golos1 = self.lan_jogo.jog_golos_clube1
		golos2 = ""
		if  self.lan_jogo.jog_golos_clube2 != None:
			golos2 = self.lan_jogo.jog_golos_clube2
			
		return "#%s, %s %s - %s %s" % (str(self.lan_numero), self.lan_jogo.jog_clube1.clu_nome_curto, golos1, golos2, self.lan_jogo.jog_clube2.clu_nome_curto)

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.lan_nome == other.lan_nome
		else:
			return False
	
	def __str__( self ):
		return self.lan_nome.encode( "utf-8" )


###########
## FONTE ##
###########

class Fonte(db.Model): 

	fon_numero_visitas = db.IntegerProperty() 
	fon_ultima_alteracao = db.DateTimeProperty() 
	fon_nome = db.StringProperty() 
	fon_link = db.LinkProperty() 
	fields = [{'Nº visitas':'fon_numero_visitas'},
			   {'Última alteração':'fon_ultima_alteracao'},
				{'Nome':'fon_nome'},
				{'Link':'fon_link'}]

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.fon_nome == other.fon_nome
		else:
			return False

	def __str__( self ):
		return self.fon_nome.encode( "utf-8" )

################
## COMENTADOR ##
################

class Comentador(db.Model): 

	com_numero_visitas = db.IntegerProperty() 
	com_ultima_alteracao = db.DateTimeProperty() 
	com_nome = db.StringProperty() 
	com_link_foto = db.StringProperty() 
	com_link = db.LinkProperty() 
	com_fonte = db.ReferenceProperty(Fonte,
	 	required=True,
      collection_name='fon_comentadores')

	fields = [{'Nº visitas':'com_numero_visitas'},
			    {'Última alteração':'com_ultima_alteracao'},
				 {'Nome':'com_nome'},
	          {'Foto':'com_link_foto'},
	          {'Link':'com_link'},
				 {'Fonte':'com_fonte'}]

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.com_nome == other.com_nome
		else:
			return False

	def __str__( self ):
		return self.com_nome.encode( "utf-8" )

class ClubeTemJogador(db.Model): 

	ctj_clube = db.ReferenceProperty(Clube,
	 	required=True,
      collection_name='clu_jogadores')
	ctj_jogador = db.ReferenceProperty(Jogador,
		required=True,
      collection_name='jgd_clubes')
	ctj_epocas = db.ListProperty(db.Key)
	ctj_numero = db.IntegerProperty() 

	fields = [{'Clube':'ctj_clube'},
				 {'Jogador':'ctj_jogador'},
				 {'Épocas':'ctj_epocas'},
				 {'Número de camisola':'ctj_numero'}]

	def __str__( self ):
		name = u"%s:%s" % (
			self.ctj_clube.__str__().decode("utf-8"),
			self.ctj_jogador.__str__().decode("utf-8"))
		return name.encode( "utf-8" )
		

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.__str__() == other.__str__()
		else:
			return False

class ClubeJogaCompeticao(db.Model): 

	cjc_clube = db.ReferenceProperty(Clube,
	 	required=True,
      collection_name='clu_competicoes')
	cjc_competicao = db.ReferenceProperty(Competicao,
		required=True,
      collection_name='cmp_clubes')
	cjc_classificacao_anterior = db.IntegerProperty()

	fields = [{'Clube':'cjc_clube'},
	          {'Competição':'cjc_competicao'},
	          {'Classificação anterior':'cjc_classificacao_anterior'}
	]

	def __str__( self ):
		name = u"%s:%s" % (
			self.cjc_clube.__str__().decode("utf-8"),
			self.cjc_competicao.__str__().decode("utf-8"))
		return name.encode( "utf-8" )

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.__str__() == other.__str__()
		else:
			return False

class JogadorJogaJogo(db.Model): 

	jjj_jogador = db.ReferenceProperty(Jogador,
	 	required=True,
      collection_name='jgd_jogos')
	jjj_jogo = db.ReferenceProperty(Jogo,
		required=True,
      collection_name='jog_jogadores')
	jjj_clube = db.ReferenceProperty(Clube,
		required=True)
	
	jjj_amarelo_minuto =  db.IntegerProperty()
	jjj_duplo_amarelo_minuto =  db.IntegerProperty()
	jjj_vermelho_minuto  =  db.IntegerProperty()
	jjj_golos_minutos =  db.ListProperty(int) 
	jjj_golos_tipos =  db.StringListProperty() 
	jjj_golos_link_videos = db.ListProperty(db.Text)
	jjj_substituicao_entrada =  db.IntegerProperty()
	jjj_substituicao_saida =  db.IntegerProperty()
	jjj_posicao = db.StringProperty()

	fields = [{'Jogador':'jjj_jogador'},
	          {'Jogo':'jjj_jogo'},
	          {'Pelo clube':'jjj_clube'},
	          {'Posição':'jjj_posicao'},
	          {'Amarelo':'jjj_amarelo_minuto'},
              {'Duplo Amarelo':'jjj_duplo_amarelo_minuto'},
	          {'Vermelho':'jjj_vermelho_minuto'},
	          {'Minutos Golos':'jjj_golos_minutos'},
	          {'Tipos Golos':'jjj_golos_tipos'},
	          {'Link Vídeos dos Golos':'jjj_golos_link_videos'},
	          {'Substituição - Minuto de entrada':'jjj_substituicao_entrada'},
	          {'Substituição - Minuto de saída':'jjj_substituicao_saida'}]

	def __str__( self ):
		name = u"%s:%s" % (
			self.jjj_jogador.__str__().decode("utf-8"),
			self.jjj_jogo.__str__().decode("utf-8"))
		return name.encode( "utf-8" )

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.__str__() == other.__str__()
		else:
			return False
	
class ComentadorComentaLance(db.Model): 

	ccl_comentador = db.ReferenceProperty(Comentador,
	 	required=True,
      collection_name='com_lances')
	ccl_lance = db.ReferenceProperty(Lance,
		required=True,
      collection_name='lan_comentadores')
	ccl_descricao = db.TextProperty()
	# 0, 1, 2, 3 - 0 é null, 1 é bem, 2 é benefício casa, 3 é benefício visitante, 
	# 4 é benefício da dúvida 
	ccl_decisao =  db.IntegerProperty() 

	fields = [{'Comentador':'ccl_comentador'},
	          {'Lance':'ccl_lance'},
	          {'Descrição':'ccl_descricao'},
	          {'Decisão':'ccl_decisao'}]

	def __str__( self ):
		name = u"%s:%s" % (
			self.ccl_comentador.__str__().decode("utf-8"),
			self.ccl_lance.__str__().decode("utf-8"))
		return name.encode( "utf-8" )

	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.__str__() == other.__str__()
		else:
			return False

class JogadorEmLance(db.Model): 

	jel_jogador = db.ReferenceProperty(Jogador,
	 	required=True,
      collection_name='jgd_lances')
	jel_lance = db.ReferenceProperty(Lance,
		required=True,
      collection_name='lan_jogadores')
	jel_papel = db.StringProperty(
		choices=("ataque", "defesa","marcador_golo",
		"comete_falta","sofre_falta",
		"comete_agressao","sofre_agressao",
		"ve_cartao","em_fora_de_jogo",
		"comete_penalti","sofre_penalti") )

	translation = {'ataque': "Ataque", "defesa": "Defesa",
	"marcador_golo":"Marcador de golo",
	"comete_falta":"Comete falta", 
	"comete_agressao":"Comete agressão", 
	"comete_penalti":"Comete penalti", 
	"sofre_falta":"Sofre falta",
	"sofre_penalti":"Sofre penalti",
	"sofre_agressao":"Sofre agressão",
	"ve_cartao":"Vê cartão",
	"em_fora_de_jogo":"Em fora de jogo"
	}
	fields = [{'Jogador':'jel_jogador'},
	          {'Lance':'jel_lance'},
				 {'Papel':'jel_papel'}]

	def __str__( self ):
		name = u"%s:%s" % (
			self.jel_jogador.__str__().decode("utf-8"),
			self.jel_lance.__str__().decode("utf-8"))
		return name


	def __eq__(self, other) : 
		if other == None:
			return False
		if type(other) == type(""):
			return False
		if other.kind() == self.kind():
			return self.__str__() == other.__str__()
		else:
			return False
			
class CacheHTML(db.Model):
	cch_namespace = db.StringProperty(
		choices=('homepage',
		'detalhe_clube',
			'detalhe_clube_jogadores',
			'detalhe_clube_jogos',
			'detalhe_clube_lances',
			'detalhe_clube_indices',
			'detalhe_clube_arbitros',
			'detalhe_clube_sumario',
		'detalhe_epoca',
			'detalhe_epoca_jogos',
			'detalhe_epoca_jogadores',
			'detalhe_epoca_clubes',
			'detalhe_epoca_arbitros',
			'detalhe_epoca_sumario',
			'detalhe_epoca_indices',
		'detalhe_competicao',
			'detalhe_competicao_jogadores',
			'detalhe_competicao_arbitros',
			'detalhe_competicao_jogos',
			'detalhe_competicao_clubes',
			'detalhe_competicao_sumario',
			'detalhe_competicao_indices',
		'detalhe_jornada',
		'detalhe_jogo',
		'detalhe_lance',
		'detalhe_arbitro',
			'detalhe_arbitro_jogadores',
			'detalhe_arbitro_clubes',
			'detalhe_arbitro_lances',
			'detalhe_arbitro_jogos',
			'detalhe_arbitro_sumario',
		'detalhe_jogador',
			'detalhe_jogador_arbitros',
			'detalhe_jogador_lances',
			'detalhe_jogador_jogos',
			'detalhe_jogador_sumario',

			'icc','ica','detalhe_icc','classificacao','tabela_icc',
			'top_arbitros','top_clubes','top_jogadores','top_jogos',
			'rss')
		)
	cch_title = db.StringProperty()
	cch_url = db.StringProperty()
	cch_signature = db.StringProperty()
	cch_date = db.DateTimeProperty()
	cch_content = db.BlobProperty()
	
	def get_admin_url(self):
		# converter detalhe_XXXXX?id=YYY até /admin/XXXXX/edit?id=YYYY
		return self.cch_url

class CacheDados(db.Model):
	ccd_namespace = db.StringProperty(
		choices=('homepage',
			'detalhe_competicao','detalhe_jornada','detalhe_jogo','detalhe_lance',
			'detalhe_arbitro','detalhe_clube','detalhe_jogador',
			'icc','ica','detalhe_icc','classificacao','tabela_icc',
			'top_arbitros','top_clubes','top_jogadores','top_jogos',
			'rss')
		)
	ccd_title = db.StringProperty()
	ccd_url = db.StringProperty()
	ccd_signature = db.StringProperty()
	ccd_date = db.DateTimeProperty()
	ccd_content = DictProperty()	
	
	def get_admin_url(self):
		# converter detalhe_XXXXX?id=YYY até /admin/XXXXX/edit?id=YYYY
		return self.ccd_url
	

class AcumuladorJornada(db.Model):
	acuj_versao = db.IntegerProperty()
	acuj_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_acumulador_jornadas')
	acuj_competicao = db.ReferenceProperty(Competicao,
	 	required=True,
      collection_name='cmp_acumulador_jornadas')
	acuj_jornada =  db.ReferenceProperty(Jornada,
	 	required=True,
      collection_name='jor_acumulador_jornadas')
	acuj_date = db.DateTimeProperty()
	acuj_content = DictProperty()
	
	fields = [{'Versão':'acuj_versao'},
				 {'Época':'acuj_epoca'},
				 {'Competição':'acuj_competicao'},
				 {'Jornada':'acuj_jornada'},
				 {'Data':'acuj_date'},
				 {'Conteúdo':'acuj_content'}]

	def __str__( self ):
		name = u"%s:%s" % (
			self.acuj_jornada.__str__().decode("utf-8"),
			self.acuj_versao)
		return name.encode( "utf-8" )

class AcumuladorCompeticao(db.Model):
	acuc_versao = db.IntegerProperty()
	acuc_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_acumulador_competicoes')
	acuc_competicao = db.ReferenceProperty(Competicao,
	 	required=True,
      collection_name='cmp_acumulador_competicoes')
	acuc_namespace = db.StringProperty(
		choices=('arbitro','clube','jogador','lance','jogo',
		'classificacao_real','classificacao_virtual','icc','ica','tabela_icc',
		'top_clubes','top_arbitros','top_jogadores','top_lances','top_jogos',
		#OBSOLETO
		'matriz_arbitro_clube')
	)
	acuc_date = db.DateTimeProperty()
	acuc_content = DictProperty()

	# para iterar pelo task_queue
	acuc_namespaces = ["arbitro", "jogo","jogador","clube", 
			"top_arbitros","top_clubes", "top_jogos", "top_jogadores",
			"classificacao_real","classificacao_virtual",
			"tabela_icc","icc","ica"]
	
	fields = [{'Versão':'acuc_versao'},
				 {'Época':'acuc_epoca'},
				 {'Competição':'acuc_competicao'},
				 {'Namespace':'acuc_namespace'},
				 {'Data':'acuc_date'},
				 {'Conteúdo':'acuc_content'}]
	

	def __str__( self ):
		name = u"%s:%s:%s" % (
			self.acuc_competicao.__str__().decode("utf-8"),
			self.acuc_versao, self.acuc_namespace)
		return name.encode( "utf-8" )


class AcumuladorEpoca(db.Model):
	acue_versao = db.IntegerProperty()
	acue_epoca = db.ReferenceProperty(Epoca,
	 	required=True,
      collection_name='epo_acumulador_epocas')
	acue_namespace = db.StringProperty(
		choices=('arbitro','clube','jogador','lance','jogo',
		'icc','tabela_icc','ica',
		'top_clubes','top_arbitros','top_jogadores','top_lances','top_jogos',
		# OBSOLETO
		'matriz_arbitro_clube')
	)
	acue_date = db.DateTimeProperty()
	acue_content = DictProperty()

	acue_namespaces = ["arbitro", "jogo","jogador","clube", 
			"top_arbitros","top_clubes", "top_jogos", "top_jogadores",
			"tabela_icc","icc","ica"]

	fields = [{'Versão':'acue_versao'},
				 {'Época':'acue_epoca'},
				 {'Namespace':'acue_namespace'},
				 {'Data':'acue_date'},
				 {'Conteúdo':'acue_content'}]
	
	def __str__( self ):
		name = u"%s:%s:%s" % (
			self.acue_epoca.__str__().decode("utf-8"),
			self.acue_versao, self.acue_namespace)
		return name.encode( "utf-8" )

# vai à memcache, depois vai à DB
def getAcumuladorCompeticao(competicao, versao, namespace):
	obj = memcache.get("acumulador-%s-%s" % (competicao, versao),
		 namespace=namespace)
	if not obj:
		obj = AcumuladorCompeticao.all().filter( \
			 "acuc_competicao = ", competicao).filter("acuc_versao = ", versao).filter("acuc_namespace = ", namespace).get()
	if obj:
		memcache.set("acumulador-%s-%s" % (competicao, versao),
		 obj, namespace=namespace, time=86400)
		return obj
	return None
	
# vai à memcache, depois vai à DB
def getAcumuladorEpoca(epoca, versao, namespace):
	obj = memcache.get("acumulador-%s-%s" % (epoca, versao),
		 namespace=namespace)
	if not obj:
		obj = AcumuladorEpoca.all().filter( \
			 "acue_epoca = ", epoca).filter("acue_versao = ", versao).filter("acue_namespace = ", namespace).get()
	if obj:
		memcache.set("acumulador-%s-%s" % (epoca, versao),
		 obj, namespace=namespace, time=86400)
		return obj
	return None

def slugify(value):
    """
    Adapted from Django's django.template.defaultfilters.slugify.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

class Post(db.Model):
    title = db.StringProperty()
    slug = db.StringProperty()
    pub_date = db.DateTimeProperty(auto_now_add=True)
    author = db.UserProperty(auto_current_user_add=True)

    excerpt = db.TextProperty(default=None)
    body = db.TextProperty()
    excerpt_html = db.TextProperty(default=None)
    body_html = db.TextProperty()
    tags = db.StringListProperty()

    def get_absolute_url(self):
        return "/blog/%04d/%02d/%02d/%s" % (self.pub_date.year,
	                                            self.pub_date.month,
	                                            self.pub_date.day,
	                                            self.slug)

    def get_edit_url(self):
        return "/admin/post/edit/%04d/%02d/%02d/%s" % (self.pub_date.year,
	                                                       self.pub_date.month,
	                                                       self.pub_date.day,
	                                                       self.slug)

    def put(self):
        """
	        Make sure that the slug is unique for the given date before
	        the data is actually saved.
        """

        # Delete the cached archive list if we are saving a new post
        if not self.is_saved():
            memcache.delete('archive_list')

        # Delete the cached tag list whenever a post is created/updated
        memcache.delete('tag_list')

        self.test_for_slug_collision()
        self.populate_html_fields()

        key = super(Post, self).put()
        return key

    def test_for_slug_collision(self):
        # Build the time span to check for slug uniqueness
        start_date = datetime.datetime(self.pub_date.year,
                                       self.pub_date.month,
                                       self.pub_date.day)
        time_delta = datetime.timedelta(days=1)
        end_date = start_date + time_delta

        # Create a query to check for slug uniqueness in the specified time span
        query = Post.all(keys_only=True)
        query.filter('pub_date >= ', start_date)
        query.filter('pub_date < ', end_date)
        query.filter('slug = ', self.slug)

        # Get the Post Key that match the given query (if it exists)
        post = query.get()

        # If any slug matches were found then an exception should be raised
        if post and (not self.is_saved() or self.key() != post):
            raise SlugConstraintViolation(start_date, self.slug)

    def populate_html_fields(self):
        # Setup Markdown with the code highlighter
        md = markdown.Markdown(extensions=['codehilite'])

        # Convert the excerpt and body Markdown into html
        if self.excerpt != None:
            self.excerpt_html = md.convert(self.excerpt)
        if self.body != None:
            self.body_html = md.convert(self.body)

class SlugConstraintViolation(Exception):
    def __init__(self, date, slug):
        super(SlugConstraintViolation, self).__init__("Slug '%s' is not unique for date '%s'." % (slug, date.date()))
