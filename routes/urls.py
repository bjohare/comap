from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
import views

urlpatterns = patterns('',
    url(r'^$', login_required(TemplateView.as_view(template_name='routes/list.html'))),
    url(r'^create/$', login_required(TemplateView.as_view(template_name='routes/create.html'))),
    url(r'^edit/(?P<fid>\d+)/$', login_required(TemplateView.as_view(template_name='routes/edit.html'))),
)
