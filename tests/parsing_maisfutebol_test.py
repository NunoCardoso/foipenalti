# -*- coding: utf-8 -*-
import os, sys
cmd_folder = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cmd_folder)
sys.path.append( cmd_folder+"/..")

from externals.parse_maisfutebol import ParseMaisFutebol

f = open(os.path.dirname(os.path.abspath(__file__))+"/83726.html", "r")
html = f.read()
f.close()

response = ParseMaisFutebol().parse(html)

assert response["status"] == "OK"
results = response["message"]

#return {"tacticas_clube1":tacticas_equipa1,
#		"tacticas_clube2":tacticas_equipa2,
#		"clube1":nome_equipa1,
#		"clube2":nome_equipa2,
#		"jogadores_titulares_clube1":jog_tit_equipa1_arr,
#		"jogadores_titulares_clube2":jog_tit_equipa2_arr,
#		"jogadores_suplentes_clube1":jog_supl_equipa1_arr,
#		"jogadores_suplentes_clube2":jog_supl_equipa2_arr,
#		"substituicoes_clube1":jog_subs_equipa1_arr,
#		"substituicoes_clube2":jog_subs_equipa2_arr,
#		"cartoes_clube1":jog_cart_equipa1_arr,
#		"cartoes_clube2":jog_cart_equipa2_arr,
#		"golos":jog_gol_arr}
	

assert results["clube1"] == "Marítimo", results["clube1"]
assert results["clube2"] == "Rio Ave", results["clube2"]
assert results["tacticas_clube1"] == "4x3x3", results["tacticas_clube1"]
assert results["tacticas_clube2"] == "4x2x3x1", results["tacticas_clube2"] 
assert results["jogadores_titulares_clube1"] == [{'numero': 1, 'nome': 'Pe\xc3\xa7anha'}, 
	{'numero': 21, 'nome': 'Briguel'}, {'numero': 16, 'nome': 'Roberge'}, {'numero': 3, 'nome': 'Robson'}, 
	{'numero': 41, 'nome': 'R\xc3\xbaben Ferreira'}, {'numero': 8, 'nome': 'Roberto Souza'}, 
	{'numero': 25, 'nome': 'Rafael Miranda'}, {'numero': 13, 'nome': 'Olberdam'}, 
	{'numero': 30, 'nome': 'Danilo Dias'}, {'numero': 9, 'nome': 'Baba'}, {'numero': 17, 'nome': 'Sami'}] , results["jogadores_titulares_clube1"]

assert results["jogadores_titulares_clube2"] == [{'numero': 38, 'nome': 'Paulo Santos'}, 
	{'numero': 18, 'nome': 'Z\xc3\xa9 Gomes'}, {'numero': 2, 'nome': 'Gaspar'}, {'numero': 5, 'nome': 'Jeferson'}, 
	{'numero': 15, 'nome': 'Tiago Pinto'}, {'numero': 8, 'nome': 'Tarantini'}, {'numero': 30, 'nome': 'Wires'}, 
	{'numero': 7, 'nome': 'Kelvin'}, {'numero': 25, 'nome': 'Jorginho'}, {'numero': 88, 'nome': 'Yazalde'}, 
	{'numero': 9, 'nome': 'Jo\xc3\xa3o Tom\xc3\xa1s'}], results["jogadores_titulares_clube2"]

assert results["jogadores_suplentes_clube1"] ==  [{'numero': 81, 'nome': 'Benachour'}, 
	{'numero': 11, 'nome': 'Ibrahim'}, {'numero': 44, 'nome': 'Jo\xc3\xa3o Guilherme'}, 
	{'numero': 18, 'nome': 'Lu\xc3\xads Olim'}, {'numero': 0, 'nome': 'F\xc3\xa1bio Fel\xc3\xadcio'}, 
	{'numero': 20, 'nome': 'Heldon'}, {'numero': 77, 'nome': 'Romain Salin'}], results["jogadores_suplentes_clube1"]

assert results["jogadores_suplentes_clube2"] == [{'numero': 11, 'nome': 'Braga'}, {'numero': 16, 'nome': 'Dinei'}, 
	{'numero': 20, 'nome': 'Atsu'}, {'numero': 17, 'nome': 'Saulo'}, {'numero': 33, 'nome': '\xc3\x89der Monteiro'},
	{'numero': 10, 'nome': 'V\xc3\xadtor Gomes'}, {'numero': 28, 'nome': 'Huanderson'}], results["jogadores_suplentes_clube2"]

# SUBSTITUICOES

assert results["substituicoes_clube1"]  == [{'jogador_saida': 'Rafael Miranda', 'jogador_entrada': 'Benachour', 
	'minuto': 57}, {'jogador_saida': 'Baba', 'jogador_entrada': 'Heldon', 'minuto': 82}, {'jogador_saida': 'Danilo Dias',
	'jogador_entrada': 'Jo\xc3\xa3o Guilherme', 'minuto': 90}], results["substituicoes_clube1"]

assert results["substituicoes_clube2"] == [{'jogador_saida': 'Jorginho', 'jogador_entrada': 'V\xc3\xadtor Gomes', 
	'minuto': 59}, {'jogador_saida': 'Z\xc3\xa9 Gomes', 'jogador_entrada': 'Braga', 'minuto': 65}, 
	{'jogador_saida': 'Yazalde', 'jogador_entrada': 'Atsu', 'minuto': 75}], results["substituicoes_clube2"]

# CARTOES
assert results["cartoes_clube1"]  ==  [{'cartao': u'cartao amarelo', 'minuto': 17, 'jogador': 'Robson'}, 
	{'cartao': u'cartao amarelo', 'minuto': 50, 'jogador': 'Briguel'}, {'cartao': u'cartao amarelo', 
	'minuto': 79, 'jogador': 'R\xc3\xbaben Ferreira'}, {'cartao': u'cartao amarelo', 'minuto': 90, 
	'jogador': 'Olberdam'}], results["cartoes_clube1"]
	
assert results["cartoes_clube2"] == [{'cartao': u'cartao amarelo', 'minuto': 41, 'jogador': 'Jeferson'}, 
	{'cartao': u'cartao amarelo', 'minuto': 44, 'jogador': 'Jo\xc3\xa3o Tom\xc3\xa1s'}, 
	{'cartao': u'cartao amarelo', 'minuto': 62, 'jogador': 'Tarantini'}], results["cartoes_clube2"]


assert results["golos"] == [{'minuto': 14, 'tipo': '', 'jogador': 'Baba'}, 
	{'minuto': 17, 'tipo': 'g.p.', 'jogador': 'Jo\xc3\xa3o Tom\xc3\xa1s'}, 
	{'minuto': 57, 'tipo': '', 'jogador': 'Baba'}], results["golos"]
