from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index),
    url(r'^tablenames$', tablenames),
    url(r'^(?P<table>\w+)$', table_columns),
    url(r'^add/(?P<table>\w+)$', add_value),
)
