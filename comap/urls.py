from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'comap.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'comap.views.front', name='front'),   
    url(r'^comap/waypoints/', include('waypoints.urls', namespace='waypoints')),
    url(r'^comap/admin/', include(admin.site.urls)),
)
