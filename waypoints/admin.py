from django.contrib import admin

from models import Waypoint


@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    exclude = ('the_geom', 'image_path','created', 'updated','elevation','route')
    readonly_fields = ('name','description')
    search_fields = ('name', 'route__name')
