from google.appengine.api import memcache 
from classes import *

class Constants():

    EPOCA_CORRENTE = None
    COMPETICAO_CORRENTE = None
    
    def getEpocaCorrente(self):
        if self.EPOCA_CORRENTE is None: 
            self.EPOCA_CORRENTE = memcache.get('EPOCA_CORRENTE')

        if self.EPOCA_CORRENTE is None:
            self.EPOCA_CORRENTE = Epoca.all().filter("epo_nome = ", u"2012/2013").get()
            memcache.set('EPOCA_CORRENTE', self.EPOCA_CORRENTE)

        return self.EPOCA_CORRENTE

    def getCompeticaoCorrente(self):
        if self.COMPETICAO_CORRENTE is None: 
            self.COMPETICAO_CORRENTE = memcache.get('COMPETICAO_CORRENTE')

        if self.COMPETICAO_CORRENTE is None:
            epoca = self.getEpocaCorrente()
            self.COMPETICAO_CORRENTE = epoca.epo_competicoes.filter("cmp_tipo = ", u"Liga").get()
            memcache.set('COMPETICAO_CORRENTE', self.COMPETICAO_CORRENTE)

        return self.COMPETICAO_CORRENTE

    def getUltimaEpocaNaDB(self):
        return self.getEpocaCorrente()
