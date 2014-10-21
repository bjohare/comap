from django.conf.urls import patterns, url
from waypoints import views


urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^edit/(?P<fid>\d+)/$', views.EditView.as_view(), name='edit'),
    url(r'^save/(?P<fid>\d+)?$', views.EditView.as_view(), name='edit'),
    url(r'^gpx/?$', views.UploadGPXView.as_view(), name='gpx'),
    
)
