import os
import django
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

settings.configure(TEMPLATE_DIRS =  (
    os.path.join(APP_ROOT_DIR, "templates"),
    os.path.join(APP_ROOT_DIR, "templates","admin"),
    os.path.join(APP_ROOT_DIR, "templates","arbitro"),
    os.path.join(APP_ROOT_DIR, "templates","blog"),
    os.path.join(APP_ROOT_DIR, "templates","clube"),
    os.path.join(APP_ROOT_DIR, "templates","competicao"),
    os.path.join(APP_ROOT_DIR, "templates","epoca"),
    os.path.join(APP_ROOT_DIR, "templates","gera"),
    os.path.join(APP_ROOT_DIR, "templates","homepage"),
    os.path.join(APP_ROOT_DIR, "templates","jogador")
))

def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app

appstats_CALC_RPC_COSTS = True
