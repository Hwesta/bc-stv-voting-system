from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'election.views.index'),
    # url(r'^bcstv/', 'bcstv.election.views.index'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^politicians/$', 'politicians.views.view_politicians'),
    url(r'^politicians/(\d+)/$', 'politicians.views.view_politician'),
    url(r'^politicians/add/$', 'politicians.views.add_politician'),

    url(r'^election/$', 'election.views.view_election'),
    url(r'^ballots/$', 'ballots.views.view_ballots'),

    url(r'^ridings/$', 'ridings.views.view_all_ridings'),
    url(r'^ridings/(\d+)/$', 'ridings.views.view_riding'),

    url(r'^keywords/$', 'keywords.views.keywordDisplay'),
)
