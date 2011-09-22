# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *

j1_a_apagar = Jogador.get_by_id(64006)
j2_a_ficar = Jogador.get_by_id(3114958)

j1_jogos = JogadorJogaJogo.all().filter("jjj_jogador = ", j1_a_apagar).count()
j2_jogos = JogadorJogaJogo.all().filter("jjj_jogador = ", j2_a_ficar).count()

j1_lances = JogadorEmLance.all().filter("jel_jogador = ", j1_a_apagar).count()
j2_lances = JogadorEmLance.all().filter("jel_jogador = ", j2_a_ficar).count()

j1_clubes = ClubeTemJogador.all().filter("ctj_jogador = ", j1_a_apagar).count()
j2_clubes = ClubeTemJogador.all().filter("ctj_jogador = ", j2_a_ficar).count()

print "Jogador 1: %s jogos, %s lances, %s clubes" % (j1_jogos, j1_lances, j1_clubes)
print "Jogador 2: %s jogos, %s lances, %s clubes" % (j2_jogos, j2_lances, j2_clubes)