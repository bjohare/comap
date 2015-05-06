from django.template import RequestContext, loader
from rest_framework import renderers, exceptions, parsers, status, VERSION
from rest_framework.settings import api_settings
from rest_framework.renderers import BrowsableAPIRenderer

class ComapApiRenderer(BrowsableAPIRenderer):
    
    def get_context(self, data, accepted_media_type, renderer_context):  
        context = super(ComapApiRenderer, self).get_context(data, accepted_media_type, renderer_context)
        context['display_edit_forms'] = False
        return context