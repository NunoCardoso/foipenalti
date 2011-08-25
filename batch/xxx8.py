# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
jogos = Jogo.all().order("jog_data")
for j in jogos:
	print("Jogo: %s" % j.__str__())
	for l in j.jog_lances:
		if l.lan_classe > 0:
			delattr(l, 'lan_tipo')

#xxx = Jogo.get_by_id(2407939)
#jogos = Jogo.all().filter("jog_data >= ", xxx.jog_data).order("jog_data")
	
for l in j.jog_lances:
	if l.lan_classe > 0:
		delattr(l, 'lan_tipo')

for l in j.jog_lances:
	print(getattr(l, 'lan_tipo')
	1072957