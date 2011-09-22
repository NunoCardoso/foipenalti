# -*- coding: utf-8 -*-
import logging
import sys
from externals.css2xpath import DOM
import re
import traceback

from xml.dom import minidom


class ParseMaisFutebol:
	
	def reDOM(self, val):
	#	logging.info(type(val.html()))
		return DOM(val.html().encode("utf-8"))

	def parse(self, html):

		p = re.compile(r'(?i)<script\b[^>]*?>[^>]*?<\/script>')
		#p2 = re.compile(r'<!DOCTYPE[^>]*>')

		html = re.sub(p, "",html)
		#html = re.sub(p2, "",html)

		dom = DOM(html)

		logging.info("ParseMaisFutebol: a arrancar com %s bytes de HTML" % len(html))
		
		maindiv = None

# NOMES EQUIPAS		
		try:
			maindiv = dom.find("div.ficha-content")[0]
		
			nomes_equipas = maindiv.find('div.topofichajogo >  table > tr > td.nome')
			nome_equipa1 = nomes_equipas[0].text().strip()
			nome_equipa2 = nomes_equipas[1].text().strip()
			logging.info("ParseMaisFutebol: equpias: "+nome_equipa1+" e "+nome_equipa2)
		except:
			trace = "".join(traceback.format_exc())
			logging.error("Não consegui ler div.ficha-content, nem div.topofichajogo >  table > tr > td.nome")
			logging.error(trace)
			return {"status":"Error","message":sys.exc_info()}
			
# TABELAS EQUIPAS	
		try:	
			tabelas = maindiv.find('div.equipa > table.fj2')
			tabelas_equipas = self.reDOM(tabelas[0])
		except:
			logging.error("Não consegui ler a div.equipa > table.fj2")
			trace = "".join(traceback.format_exc())
			logging.error(trace)
			return {"status":"Error","message":sys.exc_info()}

		try:
			tacticas_equipa1 = tabelas_equipas.xpath("/table/tr[position()=1]/td[position()=1]")[0].text().strip()  
			tacticas_equipa2 = tabelas_equipas.xpath("/table/tr[position()=1]/td[position()=3]")[0].text().strip()
		except:
			trace = "".join(traceback.format_exc())
			logging.error("Não consegui xpath table")
			logging.error(trace)
			return {"status":"Error","message":sys.exc_info()}
			
# TABELAS JOGADORES 
		try:
			jogadores_equipa1 = tabelas_equipas.xpath("/table/tr[position()=2]/td[position()=1]/table")[0]
			jogadores_equipa2 = tabelas_equipas.xpath("/table/tr[position()=2]/td[position()=3]/table")[0]
			suplentes_equipa1 = tabelas_equipas.xpath("/table/tr[position()=4]/td[position()=1]/table")[0]
			suplentes_equipa2 = tabelas_equipas.xpath("/table/tr[position()=4]/td[position()=3]/table")[0]
			subst_equipa1 = tabelas_equipas.xpath("/table/tr[position()=6]/td[position()=1]/table")[0]
			subst_equipa2 = tabelas_equipas.xpath("/table/tr[position()=6]/td[position()=3]/table")[0]
			cartoes_equipa1 = tabelas_equipas.xpath("/table/tr[position()=8]/td[position()=1]/table")[0]
			cartoes_equipa2 = tabelas_equipas.xpath("/table/tr[position()=8]/td[position()=3]/table")[0]

			tabelas_golos = self.reDOM(tabelas[2])

			jogadores_titulares_equipa1 = self.reDOM(jogadores_equipa1)
			jogadores_titulares_equipa2 = self.reDOM(jogadores_equipa2)
			jogadores_suplentes_equipa1 = self.reDOM(suplentes_equipa1)
			jogadores_suplentes_equipa2 = self.reDOM(suplentes_equipa2)
			substituicoes_equipa1 = self.reDOM(subst_equipa1)
			substituicoes_equipa2 = self.reDOM(subst_equipa2)
			cartoes_equipa1 = self.reDOM(cartoes_equipa1)
			cartoes_equipa2 = self.reDOM(cartoes_equipa2)

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
				elems = self.reDOM(val)
				numero = elems.xpath("/tr/td[position()=1]/strong")
				nome = elems.xpath("/tr/td[position()=2]/a")
				if numero and nome:
					try: 
						numero = int(numero[0].text().strip())
					except:
						pass
			
					jog_tit_equipa1_arr.append({"numero":numero, "nome":nome[0].text().strip()})
	 
			for idx, val in enumerate(jogadores_titulares_equipa2.find("tr")):
				elems = self.reDOM(val)
				numero = elems.xpath("/tr/td[position()=1]/strong")
				nome = elems.xpath("/tr/td[position()=2]/a")
				if numero and nome:
					try:
						numero = int(numero[0].text().strip())
					except:
						pass
				
					jog_tit_equipa2_arr.append({"numero":numero, "nome":nome[0].text().strip()})

# SUPLENTES

			for idx, val in enumerate(jogadores_suplentes_equipa1.find("tr")):
				elems = self.reDOM(val)
				numero = elems.xpath("/tr/td[position()=1]/strong")
				nome = elems.xpath("/tr/td[position()=2]/a")
				if numero and nome:
					try:
						numero = int(numero[0].text().strip())
					except:
						pass
					jog_supl_equipa1_arr.append({"numero":numero, "nome":nome[0].text().strip()})

			for idx, val in enumerate(jogadores_suplentes_equipa2.find("tr")):
				elems = self.reDOM(val)
				numero = elems.xpath("/tr/td[position()=1]/strong")
				nome = elems.xpath("/tr/td[position()=2]/a")
				if numero and nome:
					try:
						numero = int(numero[0].text().strip())
					except:
						pass
					jog_supl_equipa2_arr.append({"numero":numero, "nome":nome[0].text().strip()})

# SUBSTITUICOES

			for idx, val in enumerate(substituicoes_equipa1.find("tr")):
				elems = self.reDOM(val)
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
				elems = self.reDOM(val)
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

# CARTOES
		
			hash_cartoes = {"icarta.gif":"cartao amarelo","icartv.gif":"cartao vermelho","icartav.gif":"cartao duplo amarelo"}
		
			for idx, val in enumerate(cartoes_equipa1.find("tr")):
				elems = self.reDOM(val)
				minuto = elems.xpath("/tr/td[position()=1]")
				cartao = elems.xpath("/tr/td[position()=2]/img")[0]
				jogador = elems.xpath("/tr/td[position()=2]/a")

				if minuto and cartao and jogador:
					try:
						minuto = int(minuto[0].text().strip().replace("'",""))
					except:
						pass

					try:
						cartao = re.search("src=\".images.([^\"]*)\"", cartao.html()).group(1)
					except:
						pass
			
				jog_cart_equipa1_arr.append({"minuto":minuto, "cartao":hash_cartoes[cartao], "jogador":jogador[0].text().strip()})

			for idx, val in enumerate(cartoes_equipa2.find("tr")):
				elems = self.reDOM(val)
				minuto = elems.xpath("/tr/td[position()=1]")
				cartao = elems.xpath("/tr/td[position()=2]/img")[0]
				jogador = elems.xpath("/tr/td[position()=2]/a")

				if minuto and cartao and jogador:
					try:
						minuto = int(minuto[0].text().strip().replace("'",""))
					except:
						pass

					try:
						cartao = re.search("src=\".images.([^\"]*)\"", cartao.html()).group(1)
					except:
						pass

					jog_cart_equipa2_arr.append({"minuto":minuto, "cartao":hash_cartoes[cartao], "jogador":jogador[0].text().strip()})

# GOLOS

			for idx, val in enumerate(tabelas_golos.find("tr")):
				if idx != 0: #é um cabeçalho com resultado ao intervalo
					elems = self.reDOM(val)
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
					if re.search("(p.b.)",jogador):
						tipo="p.b."
						jogador = jogador.replace("(p.b.)","").strip()
			
					jog_gol_arr.append({"minuto":minuto, "jogador":jogador, "tipo":tipo})
	
		except:
			trace = "".join(traceback.format_exc())
			logging.error(trace)
			return {"status":"Error","message":sys.exc_info()}
			
		return {"status":"OK","message":{
			"tacticas_clube1":tacticas_equipa1,
			"tacticas_clube2":tacticas_equipa2,
			"clube1":nome_equipa1,
			"clube2":nome_equipa2,
			"jogadores_titulares_clube1":jog_tit_equipa1_arr,
			"jogadores_titulares_clube2":jog_tit_equipa2_arr,
			"jogadores_suplentes_clube1":jog_supl_equipa1_arr,
			"jogadores_suplentes_clube2":jog_supl_equipa2_arr,
			"substituicoes_clube1":jog_subs_equipa1_arr,
			"substituicoes_clube2":jog_subs_equipa2_arr,
			"cartoes_clube1":jog_cart_equipa1_arr,
			"cartoes_clube2":jog_cart_equipa2_arr,
			"golos":jog_gol_arr}
		}
