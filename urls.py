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
    url(r'^politicians/(\d+)/modify/$', 'politicians.views.modify_politician'),
    url(r'^politicians/add/$', 'politicians.views.add_politician'),
   

    url(r'^election/$', 'election.views.view_election'),

    url(r'^ballots/$', 'ballots.views.view_ballots'),
    url(r'^ballots/add/$', 'ballots.views.input_ballot'),
    url(r'^ballots/(\d+)/$', 'ballots.views.view_ballot'),

    url(r'^ridings/$', 'ridings.views.view_all_ridings'),
    url(r'^ridings/(\d+)/$', 'ridings.views.view_riding'),
    url(r'^ridings/(\d+)/modify/$', 'ridings.views.modify_riding'),
    url(r'^ridings/add/$', 'ridings.views.add_riding'),
    url(r'^ridings/add_poll/$', 'ridings.views.add_poll'),
    url(r'^ridings/(\d+)/modify_poll/$', 'ridings.views.modify_poll'),
    url(r'^ridings/polls/$', 'ridings.views.view_polls'),

    url(r'^keywords/$', 'keywords.views.keywordDisplay'),
    url(r'^addkeywords/$', 'keywords.views.submitKeywordList'),
)
