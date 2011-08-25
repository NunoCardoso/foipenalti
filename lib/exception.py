# -*- coding: utf-8 -*-

class BadParameterException(Exception):
	def __init__(self, error):
		self.error = error
	
	def __str__(self):
		return repr(self.error)


		# if not epoca: 
		# 	raise BadParameterException("A época da competicão "+values+" não consta na nossa base de dados.")
