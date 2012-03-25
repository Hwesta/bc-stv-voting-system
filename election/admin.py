from election.models import Election
from ballots.models import Ballot
from keywords.models import RidingKeywordList, RidingKeywordValue, PoliticianKeywordList, PoliticianKeywordValue
from politicians.models import Politician
from ridings.models import Riding, Poll
from django.contrib import admin

admin.site.register(Ballot)
admin.site.register(Election)
admin.site.register(Politician)
admin.site.register(PoliticianKeywordList)
admin.site.register(PoliticianKeywordValue)
admin.site.register(Poll)
admin.site.register(Riding)
admin.site.register(RidingKeywordList)
admin.site.register(RidingKeywordValue)

