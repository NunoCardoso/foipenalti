# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime
#Removing Deleted Properties from the Datastore
# - If you remove a property from your model, you will find that existing entities 
# still have the property. It will still be shown in the admin console and will 
# still be present in the datastore. To really clean out the old data, you need 
# to cycle through your entities and remove the data from each one.

# 1 - Make sure you have removed the properties from the model definition.
# 2 - If your model class inherits from db.Model, temporarily switch it to inherit 
# from db.Expando. (db.Model instances can't be modified dynamically, which is what 
# we need to do in the next step.)
# 3 - Cycle through existing entities (like described above). For each entity, use 
# delattr to delete the obsolete property and then save the entity.
# 4 - If your model originally inherited from db.Model, don't forget to change it 
# back after updating all the data.

#d = datetime.datetime(2011, 5, 13)
d = datetime.datetime(2011, 8, 26)
js = Jogo.all().filter("jog_data < ", d).order("-jog_data").fetch(1000)
count = 0
for j in js: 
	jjjs = j.jog_jogadores
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



