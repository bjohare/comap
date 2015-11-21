from django.contrib import admin

from models import Route


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    exclude = ('the_geom', 'image_file','gpx_file','created','updated')
    readonly_fields = ('name','description')
    search_fields = ['name', 'group__name']
