# -*- coding: utf-8 -*-
import os, sys

cmd_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cmd_folder)
home = cmd_folder+"/../"
sys.path.append(home)

 
#from tasks.parse_jogo import ParseJogo
from externals.parse_maisfutebol import ParseMaisFutebol

f = open(os.path.dirname(os.path.abspath(__file__))+"/"+sys.argv[1], "r")
html = f.read()
f.close()

response = ParseMaisFutebol().parse(html)

results = response["message"]
print "=== %s vs %s ===" % (results["clube1"], results["clube2"])
print "\n=== JOGADORES TITULARES DO %s (%s) ===\n" % (results["clube1"], len(results["jogadores_titulares_clube1"]) )
for idx, val in enumerate(results["jogadores_titulares_clube1"]):
	print val
print "\n=== JOGADORES TITULARES DO %s (%s) ===\n" % (results["clube2"], len(results["jogadores_titulares_clube2"]) )
for idx, val in enumerate(results["jogadores_titulares_clube2"]):
	print val
print "\n=== JOGADORES SUPLENTES DO %s (%s) ===\n" % (results["clube1"], len(results["jogadores_suplentes_clube1"]) )
for idx, val in enumerate(results["jogadores_suplentes_clube1"]):
	print val
print "\n=== JOGADORES SUPLENTES DO %s (%s) ===\n" % (results["clube2"], len(results["jogadores_suplentes_clube2"]) )
for idx, val in enumerate(results["jogadores_suplentes_clube2"]):
	print val
print "\n=== SUBSTITUIÇÕES DO %s (%s) ===\n" % (results["clube1"], len(results["substituicoes_clube1"]) )
for idx, val in enumerate(results["substituicoes_clube1"]):
	print val
print "\n=== SUBSTITUIÇÕES DO %s (%s) ===\n" % (results["clube2"], len(results["substituicoes_clube2"]) )
for idx, val in enumerate(results["substituicoes_clube2"]):
	print val
print "\n=== CARTÕES DO %s (%s) ===\n" % (results["clube1"], len(results["cartoes_clube1"]) )
for idx, val in enumerate(results["cartoes_clube1"]):
	print val
print "\n=== CARTÕES DO %s (%s) ===\n" % (results["clube2"], len(results["cartoes_clube2"]) )
for idx, val in enumerate(results["cartoes_clube2"]):
	print val	
print "\n=== GOLOS === (%s) \n" %  len(results["golos"])
for idx, val in enumerate(results["golos"]):
	print val

#print ParseJogo().parse(response)
