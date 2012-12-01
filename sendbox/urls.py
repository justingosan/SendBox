from django.conf.urls import patterns, url


urlpatterns = patterns('sendbox.views',
    url(r'^$', 'sendbox_index_view', name="sendbox_index_view"),
    url(r'^sendbox/(?P<folder_id>.*)/?$', 'sendbox_app_view', name="sendbox_app_view"),
    url(r'^process/$', 'sendbox_processor', name="sendbox_processor"),
    url(r'^get_auth_token_handler/$', 'get_auth_token_handler', name="get_auth_token_handler"),
    url(r'^logout/$', 'logout', name='logout'),
)


urlpatterns += patterns('django.views.generic.simple',
    url(r'^doc/$', 'direct_to_template', {'template': 'sendbox/guide.html'}, name="sendbox_docs"),
)
