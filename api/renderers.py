from rest_framework.renderers import BrowsableAPIRenderer

class ComapApiRenderer(BrowsableAPIRenderer):
    """Custom APIRenderer to remove editing forms from Browsable API"""
    
    def get_context(self, data, accepted_media_type, renderer_context):  
        context = super(ComapApiRenderer, self).get_context(data, accepted_media_type, renderer_context)
        context['display_edit_forms'] = False
        return context