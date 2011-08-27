# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime

js = Jogo.all()
for j in js: 
	clube1 = j.jog_clube1
	clube2 = j.jog_clube2
	clubes = []  
	for jjj in jjjs:
		count += 1
		changed = False
		if hasattr(jjj,"jjj_amarelos"):
			delattr(jjj,"jjj_amarelos")
			changed=True
		if hasattr(jjj,"jjj_amarelos_minutos"):
			delattr(jjj,"jjj_amarelos_minutos")
			changed=True
		if hasattr(jjj,"jjj_vermelhos_minutos"):
			delattr(jjj,"jjj_vermelhos_minutos")
			changed=True
		if hasattr(jjj,"jjj_golos"):
			delattr(jjj,"jjj_golos")
			changed=True
		if changed == True:
			jjj.put()
			print str(count) + ": "+str(j.jog_data)+" "+str(jjj)+" *"
		else:
			print str(count) + ": "+str(j.jog_data)+" "+str(jjj)



