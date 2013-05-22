from django.template.loader import render_to_string
import os
import config

def overquota(handler):
    handler.response.set_status(404)
    return handler.response.out.write( 
        render_to_string( 
           os.path.join(os.path.dirname(__file__),'templates','over_quota.html'), 
           {
               'host':os.environ['HTTP_HOST'],
               'settings': config.SETTINGS
           }
        ) 
    )
