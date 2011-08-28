#!/usr/bin/env python
# Copyright 2009 Google Inc.
#

import os
import re
import tempfile

from google.appengine.api import datastore
from google.appengine.ext import db
from google.appengine.ext.bulkload import transform
from google.appengine.api import datastore_types
from google.appengine.ext.bulkload.transform import *

# SimpleXML list Helpers

def string_list_from_child_node(xpath):

	#xml to gae
	def string_list_from_child_node_lambda(unused_value, bulkload_state):
		result = []
		for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
			if not node or node.text == None:
				result.append("")
			else:
				result.append(node.text)
		return result

	return string_list_from_child_node_lambda

def text_list_from_child_node(xpath):

        #xml to gae                                                                                                                        
        def text_list_from_child_node_lambda(unused_value, bulkload_state):
                result = []
                for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
                        if not node or node.text == None:
                                result.append(db.Text(""))
                        else:
                                result.append(db.Text(node.text))
                return result

        return text_list_from_child_node_lambda

def link_list_from_child_node(xpath):

    def link_list_from_child_node_lambda(unused_value, bulkload_state):
       result = []
       for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
           if node and node.text is not None:
               result.append(db.Link(node.text))
       return result

    return link_list_from_child_node_lambda

def int_list_from_child_node(xpath):

	#xml to gae
	def int_list_from_child_node_lambda(unused_value, bulkload_state):
		result = []
		for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
			if node and node is not None:
				result.append(int(node.text))
		return result

	return int_list_from_child_node_lambda


def long_list_from_child_node(xpath):

	#xml to gae
	def long_list_from_child_node_lambda(unused_value, bulkload_state):
		result = []
		for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
			if node and node is not None:
				result.append(long(node.text))
		return result

	return long_list_from_child_node_lambda

def key_list_from_child_node(xpath, kind):

	def key_list_from_child_node_lambda(unused_value, bulkload_state):
		result = []
		for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
			if node and node.text is not None:
				result.append(datastore.Key.from_path(kind, int(node.text)))
		return result

	return key_list_from_child_node_lambda


def key_list_from_child_node_empty_if_none(xpath, kind):

	def key_list_from_child_node_empty_if_none_lambda(unused_value, bulkload_state):
		result = []
		for node in bulkload_state.current_dictionary['__node__'].findall(xpath):
			if node and node.text is not None:
				result.append(datastore.Key.from_path(kind, int(node.text)))
		return result

	return key_list_from_child_node_empty_if_none_lambda


def child_node_from_list(child_node_name):

	def child_node_from_list_lambda(values):
		if values == '' or values is None:
			return []
		return [(child_node_name, str(value)) for value in values]

	return child_node_from_list_lambda

def child_node_from_list_key(child_node_name):

	def child_node_from_list_key_lambda(values):
		if values == '' or values is None:
			return []
		return [(child_node_name, transform.key_id_or_name_as_string(value)) for value in values]

	return child_node_from_list_key_lambda

def create_foreign_key_none_if_empty(kind, key_is_id=False):

	def create_foreign_key_none_if_empty_lambda(value):
		if value is None:
			return None
		if key_is_id:
			value = int(value)
		return datastore.Key.from_path(kind, value)

	return create_foreign_key_none_if_empty_lambda
	
