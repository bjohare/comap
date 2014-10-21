from django import forms
from django.contrib.gis.db import models
from waypoints.models import HeritageCycleRouteSouthWaypoints23062014 as HeritageWaypoints


class EditWaypointForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(EditWaypointForm, self).__init__(*args, **kwargs)
        # required fields
        self.fields['fid'].required = True
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True
        self.fields['elevation'].required= True
        self.fields['image_path'].required = False
        self.fields['the_geom'].required = False
        self.fields['date'].required = False
        

    class Meta:
        model = HeritageWaypoints
        fields = ['fid','name','description','latitude','longitude','elevation','image_path','the_geom','date']
        
    # stores the point geometry
    the_geom = models.PointField()

    
"""Class to handle GPX file uploads"""
class UploadGPXForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(UploadGPXForm, self).__init__(*args, **kwargs)
        # required fields
        self.fields['name'].required = True
        #self.fields['description'].required = True
        self.fields['data_type'].required = False
    
    select = [('tracks', 'Track: '),
              ('waypoints','Wapoints: ')]
        
    gpxfile = forms.FileField()
    name = forms.CharField(max_length=255)
    description = forms.Textarea()
    data_type = forms.ChoiceField(choices=select, widget=forms.RadioSelect())
    

    
    

    