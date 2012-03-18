from django.shortcuts import render_to_response
from ridings.models import Riding
from politicians.models import Politician
from keywords.models import RidingKeywordList,RidingKeywordValue,RidingKeywordListForm,RidingKeywordValueForm,PoliticianKeywordList,PoliticianKeywordValue,PoliticianKeywordListForm,PoliticianKeywordValueForm


# TODO Add decorators limiting access

# Keyword Management

def keywordDisplay(request):
    keyList = RidingKeywordList.objects.all()
    return render_to_response('keywords/view.html', {'keyword_list' : keyList})


def submitKeywordList(request):
    if request.method == 'POST':
        form = RidingKeywordListForm(request.Post)
        if form.is_valid():
            return HttpResponseRedirect('keywords/view.html')
    else:
        form = RidingKeywordListForm()
    return render_to_response('keywords/view.html',{'form':form})
