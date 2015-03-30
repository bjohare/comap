from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from api import views
from api.views import list_tracks
from django.contrib import admin
admin.autodiscover()

# api endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'waypoints', views.WaypointViewSet, base_name='waypoints')
router.register(r'media', views.WaypointMediaViewSet, base_name='media')
router.register(r'tracks', views.RouteViewSet, base_name='tracks')
router.register(r'points', views.TrackPointViewSet, base_name='points')

urlpatterns = patterns('',
    url(r'^comap/$', TemplateView.as_view(template_name='comap/index.html')),
    url(r'^comap/login/$', 'django.contrib.auth.views.login', {'template_name': 'comap/login.html'}),
    url(r'^comap/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'comap/logout.html'}),
    url(r'^comap/api/', include(router.urls, namespace='api')),
    url(r'^comap/api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^comap/api/routes', list_tracks),
    url(r'^comap/waypoints/', include('waypoints.urls', namespace='waypoints')),
    url(r'^comap/routes/', include('routes.urls', namespace='routes')),
    url(r'^grappelli/', include('grappelli.urls')), 
    url(r'^comap/admin/', include(admin.site.urls)),
)
