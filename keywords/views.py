from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from politicians.models import Politician
from keywords.models import RidingKeywordList,RidingKeywordValue,RidingKeywordListForm,RidingKeywordValueForm,PoliticianKeywordList,PoliticianKeywordValue,PoliticianKeywordListForm,PoliticianKeywordValueForm


# TODO Add decorators limiting access

# Keyword Management

def keywordDisplay(request):
    keyList = RidingKeywordValue.objects.all()
    PolList = PoliticianKeywordValue.objects.all()
    keylist = RidingKeywordList.objects.all()
    pollist = PoliticianKeywordList.objects.all()
    return render_to_response('keywords/view.html', {'keyword_list' : keyList,'pol_list' : PolList,'ridlist':keylist, 'pollist':pollist})

def submitKeywordList(request):
    if request.method == 'POST':
        form = RidingKeywordListForm(request.POST)
        if form.is_valid():
	    form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = RidingKeywordListForm()

    return render(request,'keywords/addkeywords.html',{'form':form})
