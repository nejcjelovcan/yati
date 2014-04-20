from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yati.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),

    url(r'^yati/', include('yati_api.urls')),
    url(r'^logout/', 'yati_api.views.logout', name='yati-logout'),
    url(r'', 'yati_api.views.main', name='yati-main'),
)
