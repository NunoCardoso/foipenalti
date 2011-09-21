# -*- coding: utf-8 -*-

#import the webapp module
from google.appengine.ext import webapp
from google.appengine.ext import db
from django.template.defaultfilters import removetags

from django.utils import simplejson
from django.conf import settings
import unicodedata
import datetime
import logging 
import urllib
import re
from classes import *
from lib import gera_icc_para_jogo

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

weekday = {"1":u"2ª feira",
"2":u"3ª feira",
"3":u"4ª feira",
"4":u"5ª feira",
"5":u"6ª feira",
"6":u"Sábado",
"0":u"Domingo"}

month = {"January":u"Janeiro",
"February":u"Fevereiro",
"March":u"Março",
"April":u"Abril",
"May":u"Maio",
"June":u"Junho",
"July":u"Julho",
"August":u"Agosto",
"September":u"Setembro",
"October":u"Outubro",
"November":u"Novembro",
"December":u"Dezembro"
}

short_month = {"January":u"Jan.",
"February":u"Fev.",
"March":u"Mar.",
"April":u"Abr.",
"May":u"Mai.",
"June":u"Jun.",
"July":u"Jul.",
"August":u"Ago.",
"September":u"Set.",
"October":u"Out.",
"November":u"Nov.",
"December":u"Dez."
}

#####################################
######## ATTRIBUTE / TYPE / OBJ #####
#####################################

@register.filter("attribute")
def attribute(value, arg):
	if hasattr(value, str(arg)):
		return getattr(value, arg)
	else:
		return settings.TEMPLATE_STRING_IF_INVALID

@register.filter("get_element_and_attribute")
def get_element_and_attribute(value, i, arg):
	if hasattr(value[i], str(arg)):
		return getattr(value[i], arg)
	else:
		return settings.TEMPLATE_STRING_IF_INVALID


@register.filter("getEntityByKey")
def getEntityByKey(key):
	return db.get(key)

@register.filter("get_id")
def get_id(obj):
	try:
		return obj.key().id()
	except:
		return None
		
@register.filter("gettype")
def gettype(value):
	return type(value)
	
@register.filter("islist")
def islist(value):
	return type(value) == type([])

@register.filter("hashkey")
def hashkey(dict, index):
    if index in dict:
        return dict[index]
    return None

@register.filter("get_range")
def get_range( value ):
  return range( value )
	
@register.filter("get_range_from")
def get_range_from( value, value2 ):
  return range( value, value2)

@register.filter("can_be_number")
def can_be_number( val ):
	try:
		x =  int(val)
	except:
		return False
	return True

########################
###### PATTERN MATCH ###
########################

@register.filter("startswith")
def startswith(value, arg):
	if not value:
		return False
	if type(value) == type(2L) or type(value) == type(2): 
		return False
	if type(value) == type(u""): 
		return value.startswith(arg)
	try: 
		return value.__str__().startswith(arg)
	except:
		return False

@register.filter("doesntstartswith")
def doesntstartswith(value, arg):
	if not value:
		return True
	if type(value) == type(2L) or type(value) == type(2): 
		return True
	if type(value) == type(u""): 
		if value.startswith(arg):
			return False
		else:
			return True
	try: 
		if value.__str__().startswith(arg):
			return False
		else:
			return True
	except:
		return True

@register.filter("isvideo")
def isvideo(value):
	return re.search("video",value)

@register.filter("iscomentario")
def iscomentario(value):
	return re.search("comentario",value)

@register.filter("matches")
def matches(value, pattern):
	m = re.search(pattern, value)
	if m:
		return True
	return False

###########################
######### LIST ############
###########################

@register.filter("isinintegerlist")
def isinintegerlist(intege, list):
	return intege in list

@register.filter("array_join")
def array_join(array, separator):
	return separator.join(array)

@register.filter("array_len_ne")
def array_len_ne(array, value):
	return len(array) != value
	
@register.filter("isnotinlist")
def isnotinlist(value, list):
	if value in list:
		return False
	return True

@register.filter("isinlist")
def isinlist(value, list):
	if value in list:
		return True
	return False

# inverse of isinlist
@register.filter("listcontainselement")
def listcontainselement(list,value):
	if value in list:
		return True
	return False

@register.filter("containsepocakey")
def containsepocakey(epocas_list,epoca_needle_key):
	for epoca_key in epocas_list:
		if epoca_needle_key == epoca_key:
			return True
	return False
	
@register.filter("has_element")
def has_element(list, value):
	if len(list) <= value:
		return False
	return True

@register.filter("get_element")
def get_element(list, value):
	if len(list) <= value:
		return None
	return list[value]

	
###########
### CMP ###
###########
	
@register.filter("matcheslong")
def matcheslong(value, value2):
	return value == long(value2)

@register.filter("lt")
def lt(value, value2):
	return value < value2

@register.filter("gt")
def gt(value, value2):
	return value > value2

@register.filter("gteq")
def gteq(value, value2):
	return value > value2
	
@register.filter("eq")
def eq(value, value2):
	return value == value2

@register.filter("streq")
def streq(value, value2):
	return str(value) == str(value2)

@register.filter("neq")
def neq(value, value2):
	return value != value2

@register.filter("isnotnone")
def isnotnone(value):
	return value != None

#############
#### MATH ###
#############

@register.filter("subtractfrom")
def subtractfrom(value, value2):
	return value2 - value
	
@register.filter("absvalue")
def absvalue(value):
	return abs(value)
	
@register.filter("ispositive")
def ispositive(value):
	return abs(value) == value
	
@register.filter("isnegative")
def isnegative(value):
	return abs(value) != value

@register.filter("diff")
def diff(virtual, real):
	if virtual < real: 
		return "+"+str(real-virtual)
	if virtual > real: 
		return "-"+str(virtual-real)

##################
##### PRINT ######
##################

@register.filter("filternone")
def filternone(value):
	# tem de ser nesta ordem...
	if type(value) == type(2L) or type(value) == type(2) or type(value) == type(2.0):
		return str(value)	
	if type(value) == type("") and value == "":
		return ""
	if value:
		return value
	if value == None:
		return "" 

@register.filter("show_golos")
def show_golos(array_minutos_golos, array_tipos_golos):
	new_array = []
	for idx, ar in enumerate(array_minutos_golos):
		string = str(ar)+"'"
		if array_tipos_golos and array_tipos_golos[idx] != u"":
			string = string + " " + array_tipos_golos[idx]
		new_array.append(string)
	return ", ".join(new_array)

@register.filter("stripslash")
def stripslash(string):
	return re.sub("/","",string)

@register.filter("trim")
def trim(string):
	if string:
		return string.strip()
	return string
	
@register.filter("truncatehtmllist")
def truncatehtmllist( list, size ):
	newlist = []
	for item in list:
		newlist.append(truncatehtml(item, size) )
	return newlist 
	

@register.filter("truncatehtml")
def truncatehtml(value, size):
	if type(value) == type(2L) or type(value) == type(1) or type(value) == type(db.Key()):
		return value
	
	if len(value) > size and size > 3:
		return re.sub("<","&lt;",value[0:(size-3)]) + '...'
	else:
		return re.sub("<","&lt;",value[0:size])

@register.filter("urlencode")
def urlencode(value):
	return re.sub("&","%38",urllib.quote(value))

@register.filter("print_icc")
def print_icc(jogo):
	if jogo.jog_icc == None:
		return "--"
	if not jogo.jog_clube_beneficiado and not jogo.jog_clube_prejudicado:
		return ""+str(jogo.jog_icc)+"/"+str(jogo.jog_icc)
	if jogo.jog_clube_beneficiado.key() == jogo.jog_clube1.key():
		return ""+str(jogo.jog_icc)+"/-"+str(jogo.jog_icc)
	if jogo.jog_clube_beneficiado.key() == jogo.jog_clube2.key():
		return "-"+str(jogo.jog_icc)+"/"+str(jogo.jog_icc)

@register.filter("print_icc4clube")
def print_icc(jogo, clube):
	if jogo.jog_icc == None:
		return "--"
	if not jogo.jog_clube_beneficiado and not jogo.jog_clube_prejudicado:
		return str(jogo.jog_icc)
	if jogo.jog_clube_beneficiado == clube:
		return "<B><span style='color:green;'>-"+str(jogo.jog_icc)+"</span></B>"
	if jogo.jog_clube_prejudicado == clube:
		return "<B><span style='color:red;'>"+str(jogo.jog_icc)+"</span></B>"

@register.filter("generate_icc4clube")
def generate_icc4clube(jogo, clube):
	if jogo.jog_icc == None:
		return 0
	if jogo.jog_clube_beneficiado == clube:
		return -1 * jogo.jog_icc
	return jogo.jog_icc

@register.filter("print_jog_clubes")
def print_jog_clubes(lista):
	l = []
	for clube in lista:
		l.append(Clube.get_by_id(clube.id()).clu_nome_curto)
	return ", ".join(l)

@register.filter("print_epocas_keys")
def print_epocas_keys(lista):
	l = []
	for key in lista:
		l.append(Epoca.get_by_id(key.id()).epo_nome)
	return ", ".join(l)

@register.filter("printjogo4clube")
def printjogo4clube( jogo, clube ):
  return jogo.printjogo(clube)

@register.filter("printjogo")
def printjogo( jogo ):
  return jogo.printjogo()

@register.filter("print_row_ved")
def print_row_ved( jogo, clube ):
  if jogo.jog_golos_clube1 == None or jogo.jog_golos_clube2 == None:
	 return u"<TD>--</TD>"
  if (clube == jogo.jog_clube1 and jogo.jog_golos_clube1 > jogo.jog_golos_clube2) or\
 		(clube == jogo.jog_clube2 and jogo.jog_golos_clube2 > jogo.jog_golos_clube1):
	 	return u"<TD style='text-align:center;'><div style='width:20px;height:20px;background-color:green;'>V</div></TD>"
  if (clube == jogo.jog_clube1 and jogo.jog_golos_clube1 < jogo.jog_golos_clube2) or\
 		(clube == jogo.jog_clube2 and jogo.jog_golos_clube2 < jogo.jog_golos_clube1):
	 	return u"<TD style='text-align:center;'><div style='width:20px;height:20px;background-color:red;'>D</div></TD>"
  if  jogo.jog_golos_clube1 == jogo.jog_golos_clube2:
	 	return u"<TD style='text-align:center;'><div style='width:20px;height:20px;background-color:yellow;'>E</div></TD>"


@register.filter("printlance")
def printlance( lance ):
  return lance.printlance()

@register.filter("to_json")
def to_json(value):
	return simplejson.dumps(value)

#####################
##### TRANSLATE #####
#####################

@register.filter("translate_classe")
def translate_classe(value):
	if value == None:
		return Lance.translation_classe[0]
	return Lance.translation_classe[value]

@register.filter("translate_ia")
def translate_ia(value):
	if value == None:
		return Jogo.translation_influencia_arbitro[0]
	return Jogo.translation_influencia_arbitro[value]

@register.filter("translate_ja")
def translate_ja(value):
	if value == None:
		return Jogo.translation_julgamento_arbitro[0]
	return Jogo.translation_julgamento_arbitro[value]
	
@register.filter("translate_causa")
def translate_causa(value):
	if value == None:
		return Lance.translation_causa[0]
	return Lance.translation_causa[value]

@register.filter("translate_apitado")
def translate_apitado(value):
	if value == None:
		return Lance.translation_apitado[0]
	return Lance.translation_apitado[value]

@register.filter("translate_consequencia")
def translate_consequencia(value):
	if value == None:
		return Lance.translation_consequencia[0]
	return Lance.translation_consequencia[value]

@register.filter("translate_risco_jogo")
def translate_risco_jogo(value):
	if value == None:
		return gera_icc_para_jogo.translator_descricao_risco_jogo[0]
	return gera_icc_para_jogo.translator_descricao_risco_jogo[value]

@register.filter("translate_tempo_lance")
def translate_tempo_lance(value):
	if value == None:
		return gera_icc_para_jogo.translator_descricao_tempo_lance[0]
	return gera_icc_para_jogo.translator_descricao_tempo_lance[value]

@register.filter("translate_classe_lance")
def translate_classe_lance(value):
	if value == None:
		return gera_icc_para_jogo.translator_descricao_classe_lance[0]
	return gera_icc_para_jogo.translator_descricao_classe_lance[value]


########################	
# ####### DATES ########
########################

@register.filter("pp_daymonthyear")
def pp_daymonthyear(date):
	if not date:
		return "Sem data"
	return ("%s %s %s" % ( re.sub("^0*","", date.strftime("%d")), \
				short_month[ (date.strftime("%B") ) ], \
				date.strftime("%Y") ) ) 

@register.filter("pp_dayweek_day_month")
def pp_dayweek_day_month(date):
	if not date:
		return "Sem data"
	return ("%s, %s de %s" % ( weekday[ (date.strftime("%w")) ], \
				re.sub("^0*","", date.strftime("%d")), \
				month[ (date.strftime("%B") ) ] ) ) 
 
@register.filter("pp_dayweek_day_month_year")
def pp_dayweek_day_month_year(date):
	if not date:
		return "Sem data"
	return ("%s, %s de %s de %s" % ( weekday[ (date.strftime("%w")) ], \
				re.sub("^0*","", date.strftime("%d")), \
				month[ (date.strftime("%B") ) ], 
				date.strftime("%Y") ) ) 
				
@register.filter("pp_yearmonthday")
def pp_yearmonthday(date):
	if not date:
		return "Sem data"
	return date.strftime("%Y%m%d")

@register.filter("pp_year_month_day")
def pp_year_month_day(date):
	if not date:
		return "Sem data"
	return date.strftime("%Y-%m-%d")

@register.filter("pp_year_month_day_hour_minute")
def pp_year_month_day_hour_minute(date):
	if not date:
		return "Sem data"
	return date.strftime("%Y-%m-%d %H:%M")
	
@register.filter("pp_hour")
def pp_hour(date):
	if not date:
		return "Sem data"
	string = date.strftime("%Hh%M")
	if string == "00h00":
		return ""
	return string

#########################
###### VIDEO ############
#########################

# tira o host do vídeo	
@register.filter("getvideosource")
def getvideosource(video_html):
	m = re.search("http://([^\/]*)", video_html)
	if m: 
		m2 = re.search("(\w+)\.\w+$",m.group(1))
		if m2:
			return m2.group(1)
	return "Desconhecido"	 
	
# vai à lista, tira o primeiro elementp	
@register.filter("getfirstvideo")
def getfirstvideo(list):
	if list:
		return list[0]
	return ""
	
@register.filter("resizeHeightKeepRatio")
def resizeHeightKeepRatio(value, height):
	logging.info(value)
	width = None
	height = None
	patt_width = re.compile("width=.(\d+)", re.I)
	patt_height = re.compile("height=.(\d+)", re.I)
	m = re.search(patt_width, value)
	m2 = re.search(patt_height, value)
	if m:
		width = float(m.group(1))
	if m2:
		height = float(m2.group(1))
	logging.info(width)
	logging.info(height)
	
	ratio = (float) (width / height)
	newwidth = 300.0 * ratio
	string = re.sub("height=(.)(\d+)","height=\1"+str(300),value)
	string = re.sub("width=(.)(\d+)","width=\1"+str(int(newwidth)), string)
#	logging.info(string)

	return string

@register.filter("resizewidth")
def resizewidth(value, width):	
	patt_width = re.compile("width=.(\d+)", re.I)
	return re.sub(patt_width,"width=\1"+str(width),value)

@register.filter("resizeheight")
def resizeheight(value, height):
	patt_height = re.compile("height=.(\d+)", re.I)
	return re.sub(patt_height,"height=\1"+str(height),value)

##############
### DOMAIN ###
##############

@register.filter("setdomainright")
def setdomainright(string):
	return re.sub("foipenalti\.appspot\.com","www.foipenalti.com",string)

@register.filter("ishomepage")
def ishomepage(string):
	return string == "/" or string == "/?cache=false" 

# para quando tenho QueryObjets e quero listas com elementos já recolhidos
@register.filter("query2list")
def query2list(query):
	l = []
	for o in query:
		l.append(o)
	return l
