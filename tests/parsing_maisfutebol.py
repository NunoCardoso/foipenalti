# -*- coding: utf-8 -*-
from dominic import DOM
import re

def reDOM(val):
	 return DOM("%s" % val.html())

f = open("83726.html", "r")
html = f.read()
f.close()

p = re.compile(r'(?i)<script\b[^>]*?>[^>]*?<\/script>')
p2 = re.compile(r'<!DOCTYPE[^>]*>')

html = re.sub(p, "",html)
html = re.sub(p2, "",html)

dom = DOM(html)

# EQUIPAS

maindiv = dom.find("div.ficha-content")[0]

nomes_equipas = maindiv.find('div.topofichajogo >  table > tr > td.nome')
nome_equipa1 = nomes_equipas[0].text().strip()
nome_equipa2 = nomes_equipas[1].text().strip()

assert nome_equipa1 == "Marítimo"
assert nome_equipa2 == "Rio Ave"

tabelas = maindiv.find('div.equipa > table.fj2')

tabelas_equipas = reDOM(tabelas[0])

tacticas_equipa1 = tabelas_equipas.xpath("/table/tr[position()=1]/td[position()=1]")[0].text().strip()  
tacticas_equipa2 = tabelas_equipas.xpath("/table/tr[position()=1]/td[position()=3]")[0].text().strip()

# TÁCTICAS

assert tacticas_equipa1 == "4x3x3", tacticas_equipa1
assert tacticas_equipa2 == "4x2x3x1", tacticas_equipa2

# JOGADORES 

jogadores_equipa1 = tabelas_equipas.xpath("/table/tr[position()=2]/td[position()=1]/table")[0]
jogadores_equipa2 = tabelas_equipas.xpath("/table/tr[position()=2]/td[position()=3]/table")[0]
suplentes_equipa1 = tabelas_equipas.xpath("/table/tr[position()=4]/td[position()=1]/table")[0]
suplentes_equipa2 = tabelas_equipas.xpath("/table/tr[position()=4]/td[position()=3]/table")[0]
subst_equipa1 = tabelas_equipas.xpath("/table/tr[position()=6]/td[position()=1]/table")[0]
subst_equipa2 = tabelas_equipas.xpath("/table/tr[position()=6]/td[position()=3]/table")[0]
cartoes_equipa1 = tabelas_equipas.xpath("/table/tr[position()=8]/td[position()=1]/table")[0]
cartoes_equipa2 = tabelas_equipas.xpath("/table/tr[position()=8]/td[position()=3]/table")[0]

tabelas_golos = reDOM(tabelas[2])

jogadores_titulares_equipa1 = reDOM(jogadores_equipa1)
jogadores_titulares_equipa2 = reDOM(jogadores_equipa2)
jogadores_suplentes_equipa1 = reDOM(suplentes_equipa1)
jogadores_suplentes_equipa2 = reDOM(suplentes_equipa2)
substituicoes_equipa1 = reDOM(subst_equipa1)
substituicoes_equipa2 = reDOM(subst_equipa2)
cartoes_equipa1 = reDOM(cartoes_equipa1)
cartoes_equipa2 = reDOM(cartoes_equipa2)

# JOGADORES TITULARES

jog_tit_equipa1_arr = []
jog_tit_equipa2_arr = []
jog_supl_equipa1_arr = []
jog_supl_equipa2_arr = []
jog_subs_equipa1_arr = []
jog_subs_equipa2_arr = []
jog_cart_equipa1_arr = []
jog_cart_equipa2_arr = []
jog_gol_arr = []

for idx, val in enumerate(jogadores_titulares_equipa1.find("tr")):
	 elems = reDOM(val)
	 numero = elems.xpath("/tr/td[position()=1]/strong")
	 nome = elems.xpath("/tr/td[position()=2]/a")
	 if numero and nome:
		  try: 
				numero = int(numero[0].text().strip())
		  except:
				pass
		  jog_tit_equipa1_arr.append({"numero":numero, "nome":nome[0].text().strip()})
	 

for idx, val in enumerate(jogadores_titulares_equipa2.find("tr")):
	 elems = reDOM(val)
	 numero = elems.xpath("/tr/td[position()=1]/strong")
	 nome = elems.xpath("/tr/td[position()=2]/a")
	 if numero and nome:
		  try:
				numero = int(numero[0].text().strip())
		  except:
				pass
		  jog_tit_equipa2_arr.append({"numero":numero, "nome":nome[0].text().strip()})

assert jog_tit_equipa1_arr == [{'numero': 1, 'nome': 'Pe\xc3\xa7anha'}, {'numero': 21, 'nome': 'Briguel'}, {'numero': 16, 'nome': 'Roberge'}, {'numero': 3, 'nome': 'Robson'}, {'numero': 41, 'nome': 'R\xc3\xbaben Ferreira'}, {'numero': 8, 'nome': 'Roberto Souza'}, {'numero': 25, 'nome': 'Rafael Miranda'}, {'numero': 13, 'nome': 'Olberdam'}, {'numero': 30, 'nome': 'Danilo Dias'}, {'numero': 9, 'nome': 'Baba'}, {'numero': 17, 'nome': 'Sami'}]

assert jog_tit_equipa2_arr == [{'numero': 38, 'nome': 'Paulo Santos'}, {'numero': 18, 'nome': 'Z\xc3\xa9 Gomes'}, {'numero': 2, 'nome': 'Gaspar'}, {'numero': 5, 'nome': 'Jeferson'}, {'numero': 15, 'nome': 'Tiago Pinto'}, {'numero': 8, 'nome': 'Tarantini'}, {'numero': 30, 'nome': 'Wires'}, {'numero': 7, 'nome': 'Kelvin'}, {'numero': 25, 'nome': 'Jorginho'}, {'numero': 88, 'nome': 'Yazalde'}, {'numero': 9, 'nome': 'Jo\xc3\xa3o Tom\xc3\xa1s'}]

# SUPLENTES

for idx, val in enumerate(jogadores_suplentes_equipa1.find("tr")):
	 elems = reDOM(val)
	 numero = elems.xpath("/tr/td[position()=1]/strong")
	 nome = elems.xpath("/tr/td[position()=2]/a")
	 if numero and nome:
		  try:
				numero = int(numero[0].text().strip())
		  except:
				pass
		  jog_supl_equipa1_arr.append({"numero":numero, "nome":nome[0].text().strip()})


for idx, val in enumerate(jogadores_suplentes_equipa2.find("tr")):
	 elems = reDOM(val)
	 numero = elems.xpath("/tr/td[position()=1]/strong")
	 nome = elems.xpath("/tr/td[position()=2]/a")
	 if numero and nome:
		  try:
				numero = int(numero[0].text().strip())
		  except:
				pass
		  jog_supl_equipa2_arr.append({"numero":numero, "nome":nome[0].text().strip()})

assert jog_supl_equipa1_arr == [{'numero': 81, 'nome': 'Benachour'}, {'numero': 11, 'nome': 'Ibrahim'}, {'numero': 44, 'nome': 'Jo\xc3\xa3o Guilherme'}, {'numero': 18, 'nome': 'Lu\xc3\xads Olim'}, {'numero': 0, 'nome': 'F\xc3\xa1bio Fel\xc3\xadcio'}, {'numero': 20, 'nome': 'Heldon'}, {'numero': 77, 'nome': 'Romain Salin'}]

assert jog_supl_equipa2_arr == [{'numero': 11, 'nome': 'Braga'}, {'numero': 16, 'nome': 'Dinei'}, {'numero': 20, 'nome': 'Atsu'}, {'numero': 17, 'nome': 'Saulo'}, {'numero': 33, 'nome': '\xc3\x89der Monteiro'}, {'numero': 10, 'nome': 'V\xc3\xadtor Gomes'}, {'numero': 28, 'nome': 'Huanderson'}]

# SUBSTITUICOES

for idx, val in enumerate(substituicoes_equipa1.find("tr")):
	 elems = reDOM(val)
	 minuto = elems.xpath("/tr/td[position()=1]")
	 jog1 = elems.xpath("/tr/td[position()=2]/a")
	 jog2 = elems.xpath("/tr/td[position()=4]/a")

	 if minuto and jog1 and jog2:
		  try:
				minuto = int(minuto[0].text().strip().replace("'",""))
		  except:
				pass
		  jog_subs_equipa1_arr.append({"minuto":minuto, "jogador_saida":jog1[0].text().strip(), 
											"jogador_entrada":jog2[0].text().strip()})

for idx, val in enumerate(substituicoes_equipa2.find("tr")):
	 elems = reDOM(val)
	 minuto = elems.xpath("/tr/td[position()=1]")
	 jog1 = elems.xpath("/tr/td[position()=2]/a")
	 jog2 = elems.xpath("/tr/td[position()=4]/a")

	 if minuto and jog1 and jog2:
		  try:
				minuto = int(minuto[0].text().strip().replace("'",""))
		  except:
				pass
		  jog_subs_equipa2_arr.append({"minuto":minuto, "jogador_saida":jog1[0].text().strip(),
											"jogador_entrada":jog2[0].text().strip()})

assert jog_subs_equipa1_arr == [{'jogador_saida': 'Rafael Miranda', 'jogador_entrada': 'Benachour', 'minuto': 57}, {'jogador_saida': 'Baba', 'jogador_entrada': 'Heldon', 'minuto': 82}, {'jogador_saida': 'Danilo Dias', 'jogador_entrada': 'Jo\xc3\xa3o Guilherme', 'minuto': 90}]

assert jog_subs_equipa2_arr == [{'jogador_saida': 'Jorginho', 'jogador_entrada': 'V\xc3\xadtor Gomes', 'minuto': 59}, {'jogador_saida': 'Z\xc3\xa9 Gomes', 'jogador_entrada': 'Braga', 'minuto': 65}, {'jogador_saida': 'Yazalde', 'jogador_entrada': 'Atsu', 'minuto': 75}]

# CARTOES

for idx, val in enumerate(cartoes_equipa1.find("tr")):
	elems = reDOM(val)
	minuto = elems.xpath("/tr/td[position()=1]")
	cartao = elems.xpath("/tr/td[position()=2]/img")[0]
	jogador = elems.xpath("/tr/td[position()=2]/a")

	if minuto and cartao and jogador:
		try:
			minuto = int(minuto[0].text().strip().replace("'",""))
		except:
			pass

		try:
			cartao = re.search("alt=\"([^\"]*)\"", cartao.html()).group(1)
		except:
			pass
			
	jog_cart_equipa1_arr.append({"minuto":minuto, "cartao":cartao, "jogador":jogador[0].text().strip()})

for idx, val in enumerate(cartoes_equipa2.find("tr")):
	elems = reDOM(val)
	minuto = elems.xpath("/tr/td[position()=1]")
	cartao = elems.xpath("/tr/td[position()=2]/img")[0]
	jogador = elems.xpath("/tr/td[position()=2]/a")

	if minuto and cartao and jogador:
		try:
			minuto = int(minuto[0].text().strip().replace("'",""))
		except:
			pass

	try:
		cartao = re.search("alt=\"([^\"]*)\"", cartao.html()).group(1)
	except:
		pass

	jog_cart_equipa2_arr.append({"minuto":minuto, "cartao":cartao, "jogador":jogador[0].text().strip()})

assert jog_cart_equipa1_arr == [{'cartao': u'cart\xe3o amarelo', 'minuto': 17, 'jogador': 'Robson'}, {'cartao': u'cart\xe3o amarelo', 'minuto': 50, 'jogador': 'Briguel'}, {'cartao': u'cart\xe3o amarelo', 'minuto': 79, 'jogador': 'R\xc3\xbaben Ferreira'}, {'cartao': u'cart\xe3o amarelo', 'minuto': 90, 'jogador': 'Olberdam'}]
assert jog_cart_equipa2_arr == [{'cartao': u'cat\xe3o amarelo', 'minuto': 41, 'jogador': 'Jeferson'}, {'cartao': u'cat\xe3o amarelo', 'minuto': 44, 'jogador': 'Jo\xc3\xa3o Tom\xc3\xa1s'}, {'cartao': u'cat\xe3o amarelo', 'minuto': 62, 'jogador': 'Tarantini'}]

# GOLOS

for idx, val in enumerate(tabelas_golos.find("tr")):
	if idx != 0: #é um cabeçalho com resultado ao intervalo
		elems = reDOM(val)
		minuto = elems.xpath("/tr/td[position()=2]")
		jogador = elems.xpath("/tr/td[position()=3]")
		tipo=""
		
		if minuto and jogador:
			try:
				minuto = int(minuto[0].text().strip().replace("'",""))
			except:
				pass
				
		jogador = jogador[0].text()
		if re.search("(penalty)",jogador):
			tipo="g.p."
			jogador = jogador.replace("(penalty)","").strip()
			
		jog_gol_arr.append({"minuto":minuto, "jogador":jogador, "tipo":tipo})

assert jog_gol_arr == [{'minuto': 14, 'tipo': '', 'jogador': 'Baba'}, {'minuto': 17, 'tipo': 'g.p.', 'jogador': 'Jo\xc3\xa3o Tom\xc3\xa1s'}, {'minuto': 57, 'tipo': '', 'jogador': 'Baba'}]
