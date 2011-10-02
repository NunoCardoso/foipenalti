# -*- coding: utf-8 -*-
from google.appengine.ext import db
from classes import *
import datetime

entities = MyModel.all().fetch(100)
while entities:
    for entity in entities:
        # Do something with entity
    entities = MyModel.all().filter('__key__ >', entities[-1].key()).fetch(100)
