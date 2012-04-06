#Django
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import user_passes_test
#System
from politicians.models import Politician
from ridings.models import Riding
from keywords.models import RidingKeywordList, RidingKeywordValue, \
    addRidingKeywordListForm, editRidingKeywordListForm, addRidingKeywordValueForm, editRidingKeywordValueForm
from keywords.models import PoliticianKeywordList, PoliticianKeywordValue, \
    addPoliticianKeywordListForm, editPoliticianKeywordListForm, addPoliticianKeywordValueForm, editPoliticianKeywordValueForm
from election.models import define_view_permissions, permissions_or, permissions_and, permission_always


# TODO Add decorators limiting access

# Keyword Management

@user_passes_test(define_view_permissions(['EO'],['BEF']))
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

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def new_riding_keyword(request):
    if request.method == 'POST':
        form = addRidingKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(new_riding_keyword_value,args=[RidingKeywordList.objects.all().count()]))
    else:
        form = addRidingKeywordListForm()
    return render(request,'keywords/addridingkeywords.html',{'form':form})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def new_riding_keyword_value(request, k_id):
    RidingKeywordValueFormSet = formset_factory(addRidingKeywordValueForm, extra=0)
    if request.method == 'POST':
        formset = RidingKeywordValueFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        data = []
        for i in range(Riding.objects.all().count()):
            riding = Riding.objects.get(id=i+1)
            if not riding.delete:
                data.append({'riding':i+1,'keyword':k_id})
        formset = RidingKeywordValueFormSet(initial=data)

    return render(request,'keywords/addridingkeywordvalue.html',{'formset':formset,'id':k_id})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def new_politician_keyword(request):
    if request.method == 'POST':
        form = addPoliticianKeywordListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(new_politician_keyword_value,args=[PoliticianKeywordList.objects.all().count()]))
    else:
        form = addPoliticianKeywordListForm()

    return render(request,'keywords/addpoliticiankeywords.html',{'form':form})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def new_politician_keyword_value(request, k_id):
    PoliticianKeywordValueFormSet = formset_factory(addPoliticianKeywordValueForm, extra = 0)
    if request.method == 'POST':
        formset = PoliticianKeywordValueFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                form.save()
            return HttpResponseRedirect(reverse(index))
    else:
        data = []
        for i in range(Politician.objects.all().count()):
            politician = Politician.objects.get(id=i+1)
            if not politician.delete:
                data.append({'politician':i+1,'keyword':k_id})
        formset = PoliticianKeywordValueFormSet(initial=data)

    return render(request,'keywords/addpoliticiankeywordvalue.html',{'formset':formset,'id':k_id})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
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

@user_passes_test(define_view_permissions(['EO'],['BEF']))
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

@user_passes_test(define_view_permissions(['EO'],['BEF']))
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

@user_passes_test(define_view_permissions(['EO'],['BEF']))
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

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def restoreRidingKeyword(request):
    title = "Riding"
    list = RidingKeywordList.objects.filter(delete=True)
    return render(request, 'keywords/restoreridingkeyword.html', {'list':list})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def restorePoliticianKeyword(request):
    title = "Politician"
    list = PoliticianKeywordList.objects.filter(delete=True)
    return render(request, 'keywords/restorepoliticiankeyword.html', {'list':list})


