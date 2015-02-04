from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
import views

urlpatterns = patterns('',
    url(r'^list/(?P<fid>\d+)/$', login_required(TemplateView.as_view(template_name='waypoints/list.html'))),
    url(r'^create/(?P<fid>\d+)/$', login_required(TemplateView.as_view(template_name='waypoints/create.html'))),
    url(r'^edit/(?P<fid>\d+)/$', login_required(TemplateView.as_view(template_name='waypoints/edit.html'))),
)
