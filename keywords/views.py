from django.shortcuts import render_to_response
from ridings.models import Riding
from politicians.models import Politician
from keywords.models import *

# TODO Add decorators limiting access

# Keyword Management

def keywordDisplay(request):
    keyList = RidingKeywordList.objects.all()
    return render_to_response('keywords/view.html', {'keyword_list' : keyList})
