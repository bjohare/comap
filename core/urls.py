from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from api.urls import router
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()


urlpatterns = []

urlpatterns += patterns('api.views',
                        url(r'^comap/api/', include(router.urls, namespace='api')),
                        url(r'^api/', include('rest_framework.urls',
                                              namespace='rest_framework')),
                        )

urlpatterns += patterns('ui.views',
                        url(r'^comap/$', login,
                            {'template_name': 'ui/login.html'}),
                        url(r'^comap/login/$', login,
                            {'template_name': 'ui/login.html'}),
                        url(r'^comap/logout/$', logout,
                            {'template_name': 'ui/logout.html'}),
                        #url(r'^comap/api/routes', list_tracks),
                        url(r'^comap/waypoints/',
                            include('waypoints.urls', namespace='waypoints')),
                        url(r'^comap/routes/',
                            include('routes.urls', namespace='routes')),
                        url(r'^grappelli/', include('grappelli.urls')),
                        url(r'^comap/admin/', include(admin.site.urls)),
                        #url(r'^comap/docs/', include('rest_framework_swagger.urls')),
                        )
