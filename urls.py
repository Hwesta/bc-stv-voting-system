from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Home
    url(r'^$', 'election.views.index'),
    url(r'^ro_home.html$', 'election.views.ro_homepage'),
    url(r'^eo_home.html$', 'election.views.eo_homepage'),
    url(r'^reporter_home.html$', 'election.views.reporter_homepage'),
    url(r'^admin_home.html$', 'election.views.admin_homepage'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'users/login.html'}),
    #url(r'^login/$', 'election.views.login_user'),
    url(r'^logout/$', 'election.views.logout_user'),
    
    url(r'^users/$', 'users.views.index'),
    url(r'^users/add/$', 'users.views.add_user'),
    url(r'^users/(\d+)/$', 'users.views.view_user'),
    url(r'^users/(\d+)/modify/$', 'users.views.modify_user'),
    url(r'^users/(\d+)/ban/$', 'users.views.ban_user'),
    url(r'^users/(\d+)/delete/$', 'users.views.delete_user'),

    url(r'^ridings/(\d+)/politicians/$', 'politicians.views.view_politicians'),
    url(r'^ridings/(\d+)/politicians/(\d+)/$', 'politicians.views.view_politician'),
    url(r'^ridings/(\d+)/politicians/(\d+)/modify/$', 'politicians.views.modify_politician'),
    url(r'^ridings/(\d+)/politicians/add/$', 'politicians.views.add_politician'),
    url(r'^ridings/(\d+)/politicians/deleted/$', 'politicians.views.view_deleted_politicians'),

    url(r'^election/$', 'election.views.view_election'),
    url(r'^election/recount/$', 'election.views.start_recount'),
    url(r'^election/status/$', 'election.views.change_election_status'),
    url(r'^election/location/$', 'election.views.set_location'),
    url(r'^election/winners/(\d+)/$', 'election.views.calc_winners'),
    url(r'^election/all_winners/$', 'election.views.calc_all_winners'),

    url(r'^ballots/$', 'ballots.views.view_ballots'),
    url(r'^ballots/add/poll/$', 'ballots.views.choose_poll'),
    url(r'^ballots/add/(\d+)/$', 'ballots.views.input_ballot'),
    url(r'^ballots/(\d+)/$', 'ballots.views.view_ballot'),
    url(r'^ballots/verify/$', 'ballots.views.view_conflict_list'),
    url(r'^ballots/verify/(\d+)/$', 'ballots.views.compare_ballot'),

    url(r'^ridings/$', 'ridings.views.view_all_ridings'),
    url(r'^ridings/deleted_ridings/$', 'ridings.views.view_deleted_ridings'),
    url(r'^ridings/add/$', 'ridings.views.add_riding'),
    url(r'^ridings/(\d+)/$', 'ridings.views.view_riding'),
    url(r'^ridings/reports/$', 'ridings.views.all_ridings_report'),
    url(r'^ridings/(\d+)/modify/$', 'ridings.views.modify_riding'),
    url(r'^ridings/(\d+)/polls/$', 'ridings.views.view_polls'),
    url(r'^ridings/(\d+)/polls/add/$', 'ridings.views.add_poll'),
    url(r'^ridings/(\d+)/polls/(\d+)/modify/$', 'ridings.views.modify_poll'),

    url(r'^keywords/$', 'keywords.views.index'),
    url(r'^keywords/riding/add/$', 'keywords.views.new_riding_keyword'),
    url(r'^keywords/riding/values/$', 'keywords.views.new_riding_keyword_value'),
    url(r'^keywords/politician/add/$', 'keywords.views.new_politician_keyword'),
    url(r'^keywords/politician/values/$', 'keywords.views.new_politician_keyword_value'),
    url(r'^keywords/riding/(\d+)/modify/$', 'keywords.views.edit_riding_keyword'),
    url(r'^keywords/riding/modify/values/(\d+)/$', 'keywords.views.edit_riding_keyword_value'),
    url(r'^keywords/politician/(\d+)/modify/$', 'keywords.views.edit_politician_keyword'),
    url(r'^keywords/politician/modify/values/(\d+)/$', 'keywords.views.edit_politician_keyword_value'),
    url(r'^keywords/riding/restore/$', 'keywords.views.restoreRidingKeyword'),
    url(r'^keywords/politician/restore/$', 'keywords.views.restorePoliticianKeyword'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
