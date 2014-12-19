from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
from api import views
from django.contrib import admin
admin.autodiscover()

# api endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'waypoints', views.WaypointViewset, base_name='waypoints')
router.register(r'routes', views.RouteViewSet)

urlpatterns = patterns('',
    url(r'^comap/login/$', 'django.contrib.auth.views.login', {'template_name': 'comap/login.html'}),
    url(r'^comap/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'comap/logout.html'}),
    url(r'^comap/api/', include(router.urls, namespace='api')),
    url(r'^comap/api/', include('rest_framework.urls', namespace='rest_framework')), 
    url(r'^comap/waypoints/', include('waypoints.urls', namespace='waypoints')),
    url(r'^comap/gpx/', include('gpx.urls', namespace='gpx')),
    url(r'^comap/admin/', include(admin.site.urls)),
)
