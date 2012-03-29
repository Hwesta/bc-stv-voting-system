from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from politicians.models import Politician
from keywords.models import RidingKeywordList, RidingKeywordValue, \
    addRidingKeywordListForm, editRidingKeywordListForm, addRidingKeywordValueForm, editRidingKeywordValueForm
from keywords.models import PoliticianKeywordList, PoliticianKeywordValue, \
    addPoliticianKeywordListForm, editPoliticianKeywordListForm, addPoliticianKeywordValueForm, editPoliticianKeywordValueForm


# TODO Add decorators limiting access

# Keyword Management

def index(request):
    riding_keyword_values = RidingKeywordValue.objects.all()
    politician_keyword_values = PoliticianKeywordValue.objects.all()
    riding_keywords = RidingKeywordList.objects.filter(delete=False)
    politician_keywords = PoliticianKeywordList.objects.filter(delete=False)
    return render(request, 'keywords/view.html',
        {'riding_keyword_values': riding_keyword_values,
         'politician_keyword_values': politician_keyword_values,
         'riding_keywords': riding_keywords,
         'politician_keywords': politician_keywords
         })

def new_riding_keyword(request):
    if request.method == 'POST':
        form = addRidingKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = addRidingKeywordListForm()
    return render(request,'keywords/addridingkeywords.html',{'form':form})

def new_riding_keyword_value(request):
    if request.method == 'POST':
        form = addRidingKeywordValueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = addRidingKeywordValueForm()

    return render(request,'keywords/addridingkeywordvalue.html',{'form':form})

def new_politician_keyword(request):
    if request.method == 'POST':
        form = addPoliticianKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = addPoliticianKeywordListForm()

    return render(request,'keywords/addpoliticiankeywords.html',{'form':form})

def new_politician_keyword_value(request):
    if request.method == 'POST':
        form = addPoliticianKeywordValueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = addPoliticianKeywordValueForm()

    return render(request,'keywords/addpoliticiankeywordvalue.html',{'form':form})

def edit_riding_keyword(request, k_id):
    keyword = RidingKeywordList.objects.get(id=k_id)
    if request.method == 'POST':
        form = editRidingKeywordListForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = editRidingKeywordListForm(instance=keyword)
    return render(request, 'keywords/modifyridingkeywordlist.html', {'form':form,'keyword':keyword})

def edit_riding_keyword_value(request, k_id):
    keyword = RidingKeywordValue.objects.get(id=k_id)
    if request.method == 'POST':
        form = editRidingKeywordValueForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = editRidingKeywordValueForm(instance=keyword)
    return render(request, 'keywords/modifyridingkeywordvalue.html', {'form':form,'keyword':keyword})

def edit_politician_keyword(request, k_id):
    keyword = PoliticianKeywordList.objects.get(id=k_id)
    if request.method == 'POST':
        form = editPoliticianKeywordListForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = editPoliticianKeywordListForm(instance=keyword)
    return render(request, 'keywords/modifypoliticiankeywordlist.html', {'form':form,'keyword':keyword})

def edit_politician_keyword_value(request, k_id):
    keyword = PoliticianKeywordValue.objects.get(id=k_id)
    if request.method == 'POST':
        form = editPoliticianKeywordValueForm(request.POST,instance=keyword)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = editPoliticianKeywordValueForm(instance=keyword)
    return render(request, 'keywords/modifypoliticiankeywordvalue.html', {'form':form,'keyword':keyword})

def restoreRidingKeyword(request):
    title = "Riding"
    list = RidingKeywordList.objects.filter(delete=True)
    return render(request, 'keywords/restoreridingkeyword.html', {'list':list})

def restorePoliticianKeyword(request):
    title = "Politician"
    list = PoliticianKeywordList.objects.filter(delete=True)
    return render(request, 'keywords/restorepoliticiankeyword.html', {'list':list})


