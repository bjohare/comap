import logging
from django import forms

logger = logging.getLogger(__name__)

"""Class to handle Route creation"""
class RouteAddForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(RouteAddForm, self).__init__(*args, **kwargs)
        # required fields
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['gpxfile'].required = True
        self.fields['image'].required = False
        #logger.debug(self.fields)
        
    name = forms.CharField(max_length=255)
    description = forms.CharField(max_length=65000)
    gpxfile = forms.FileField()
    image = forms.ImageField()
    

    
    

    