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

def submitRidingKeywordList(request):
    if request.method == 'POST':
        form = RidingKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = RidingKeywordListForm()
    return render(request,'keywords/addridingkeywords.html',{'form':form})

def submitRidingKeywordValue(request):
    if request.method == 'POST':
        form = RidingKeywordValueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = RidingKeywordValueForm()

    return render(request,'keywords/addridingkeywordvalue.html',{'form':form})

def submitPoliticianKeywordList(request):
    if request.method == 'POST':
        form = PoliticianKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = PoliticianKeywordListForm()

    return render(request,'keywords/addpoliticiankeywords.html',{'form':form})

def submitPoliticianKeywordValue(request):
    if request.method == 'POST':
        form = PoliticianKeywordValueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = PoliticianKeywordValueForm()

    return render(request,'keywords/addpoliticiankeywordvalue.html',{'form':form})

def modifyRidingKeywordList(request, k_id):
    keyword = RidingKeywordList.objects.get(id=k_id)
    if request.method == 'POST':
        form = RidingKeywordListForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = RidingKeywordListForm(instance=keyword)
    return render(request, 'keywords/modifyridingkeywordlist.html', {'form':form,'keyword':keyword})

def modifyRidingKeywordValue(request, k_id):
    keyword = RidingKeywordValue.objects.get(id=k_id)
    if request.method == 'POST':
        form = RidingKeywordValueForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = RidingKeywordValueForm(instance=keyword)
    return render(request, 'keywords/modifyridingkeywordvalue.html', {'form':form,'keyword':keyword})

def modifyPoliticianKeywordList(request, k_id):
    keyword = PoliticianKeywordList.objects.get(id=k_id)
    if request.method == 'POST':
        form = PoliticianKeywordListForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = PoliticianKeywordListForm(instance=keyword)
    return render(request, 'keywords/modifypoliticiankeywordlist.html', {'form':form,'keyword':keyword})

def modifyPoliticianKeywordValue(request, k_id):
    keyword = PoliticianKeywordValue.objects.get(id=k_id)
    if request.method == 'POST':
        form = PoliticianKeywordValueForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(keywordDisplay))
    else:
        form = PoliticianKeywordValueForm(instance=keyword)
    return render(request, 'keywords/modifypoliticiankeywordvalue.html', {'form':form,'keyword':keyword})


