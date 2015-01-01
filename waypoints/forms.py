from django import forms
from django.contrib.gis.db import models
from waypoints.models import Waypoint


class EditWaypointForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(EditWaypointForm, self).__init__(*args, **kwargs)
        # required fields
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['elevation'].required= True
        self.fields['image_path'].required = False
        self.fields['the_geom'].required = False
        self.fields['date'].required = False
        self.fields['route'].required = True
        

    class Meta:
        model = Waypoint
        fields = ['name','description','elevation','image_path','the_geom','date','route']
        
    # stores the point geometry
    the_geom = models.PointField()

    
    

    