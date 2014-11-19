from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from api import views
from django.contrib import admin
admin.autodiscover()

# api endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'waypoints', views.WaypointViewset, base_name='waypoints')
router.register(r'layers', views.LayersViewset)

urlpatterns = patterns('',
    url(r'^comap/api/', include(router.urls, namespace='api')),
    url(r'^comap/api/', include('rest_framework.urls', namespace='rest_framework')), 
    url(r'^comap/waypoints/', include('waypoints.urls', namespace='waypoints')),
    url(r'^comap/gpx/', include('gpx.urls', namespace='gpx')),
    url(r'^comap/admin/', include(admin.site.urls)),
)
