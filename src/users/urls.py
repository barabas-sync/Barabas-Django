from django.conf.urls.defaults import *

urlpatterns = patterns('barabasdjango.users.views',
    (r'^logout/$', 'logout'),
    (r'^profile/$', 'profile'),
    (r'^signup/$', 'signup'),
    (r'^$', 'index'),
)
