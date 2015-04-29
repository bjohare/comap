from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

@admin.register(User)
class ComapUserAdmin(UserAdmin):
    #exclude = ('the_geom', 'image_file','gpx_file','created','updated')
    readonly_fields = ('username')
    

admin.site.unregister(User)
admin.site.register(User, ComapUserAdmin)
