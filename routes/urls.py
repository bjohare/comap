from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^create/$', views.RouteAddView.as_view(), name='routes'),
)
