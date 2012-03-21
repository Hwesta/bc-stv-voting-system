from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from politicians.models import Politician
from keywords.models import RidingKeywordList, RidingKeywordValue, \
    RidingKeywordListForm, RidingKeywordValueForm
from keywords.models import PoliticianKeywordList, PoliticianKeywordValue, \
    PoliticianKeywordListForm, PoliticianKeywordValueForm


# TODO Add decorators limiting access

# Keyword Management

def index(request):
    riding_keyword_values = RidingKeywordValue.objects.all()
    politician_keyword_values = PoliticianKeywordValue.objects.all()
    riding_keywords = RidingKeywordList.objects.filter(delete=False)
    politician_keywords = PoliticianKeywordList.objects.filter(delete=False)
    return render_to_response('keywords/view.html',
        {'riding_keyword_values': riding_keyword_values,
         'politician_keyword_values': politician_keyword_values,
         'riding_keywords': riding_keywords,
         'politician_keywords': politician_keywords
         })

def new_riding_keyword(request):
    if request.method == 'POST':
        form = RidingKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = RidingKeywordListForm()
    return render(request,'keywords/addridingkeywords.html',{'form':form})

def new_riding_keyword_value(request):
    if request.method == 'POST':
        form = RidingKeywordValueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = RidingKeywordValueForm()

    return render(request,'keywords/addridingkeywordvalue.html',{'form':form})

def new_politician_keyword(request):
    if request.method == 'POST':
        form = PoliticianKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = PoliticianKeywordListForm()

    return render(request,'keywords/addpoliticiankeywords.html',{'form':form})

def new_politician_keyword_value(request):
    if request.method == 'POST':
        form = PoliticianKeywordValueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = PoliticianKeywordValueForm()

    return render(request,'keywords/addpoliticiankeywordvalue.html',{'form':form})

def edit_riding_keyword(request, k_id):
    keyword = RidingKeywordList.objects.get(id=k_id)
    if request.method == 'POST':
        form = RidingKeywordListForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = RidingKeywordListForm(instance=keyword)
    return render(request, 'keywords/modifyridingkeywordlist.html', {'form':form,'keyword':keyword})

def modifyRidingKeywordValue(request, k_id):
    keyword = RidingKeywordValue.objects.get(id=k_id)
    if request.method == 'POST':
        form = RidingKeywordValueForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = RidingKeywordValueForm(instance=keyword)
    return render(request, 'keywords/modifyridingkeywordvalue.html', {'form':form,'keyword':keyword})

def modifyPoliticianKeywordList(request, k_id):
    keyword = PoliticianKeywordList.objects.get(id=k_id)
    if request.method == 'POST':
        form = PoliticianKeywordListForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = PoliticianKeywordListForm(instance=keyword)
    return render(request, 'keywords/modifypoliticiankeywordlist.html', {'form':form,'keyword':keyword})

def modifyPoliticianKeywordValue(request, k_id):
    keyword = PoliticianKeywordValue.objects.get(id=k_id)
    if request.method == 'POST':
        form = PoliticianKeywordValueForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = PoliticianKeywordValueForm(instance=keyword)
    return render(request, 'keywords/modifypoliticiankeywordvalue.html', {'form':form,'keyword':keyword})

def restoreRidingKeyword(request):
	title = "Riding"
	list = RidingKeywordList.objects.filter(delete=True)
	return render_to_response('keywords/restoreridingkeyword.html', {'list':list})

def restorePoliticianKeyword(request):
	title = "Politician"
	list = PoliticianKeywordList.objects.filter(delete=True)
	return render_to_response('keywords/restorepoliticiankeyword.html', {'list':list})


