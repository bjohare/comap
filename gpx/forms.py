from django import forms

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
    

    
    

    