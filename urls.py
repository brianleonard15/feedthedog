from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
views = "experiment.views." 

urlpatterns = patterns('',
    (r'^$',                 views + 'login_user'),
    (r'^logout/$',          views + 'logout_user'),
    (r'^consent/$',         views + 'consent'),
    (r'^instructions/$',    views + 'instructions'),
    (r'^examples/$',        views + 'examples'),
    (r'^training/$',        views + 'training'),
    (r'^training/review/$', views + 'training_review'),
    (r'^experiment/$',      views + 'experiment'),
    (r'^diagnostics/',      views + 'diagnostics'),
    (r'^payment/',          views + 'payment'),
)

urlpatterns += staticfiles_urlpatterns()
