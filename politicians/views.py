from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import user_passes_test
from ridings.models import Riding
from politicians.models import Politician, Politician_Add_Form, Politician_Modify_Form
from keywords.models import PoliticianKeywordValue, PoliticianKeywordList,addPoliticianKeywordValueForm
from election.models import define_view_permissions, permissions_or, permissions_and, permission_always

# TODO Add decorators limiting access

# Candidate/Incumbent Information
# NOTE Should we have one set of functions for incumbents and candidates,
# and just display different info based on a flag?

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_all_politicians(request):
    t = "Politicians"
    p = Politician.objects.filter(delete=False)
    return render(request, 'politicians/politicians.html',
            {'politicians': p, 'type':t})

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_politician(request, p_id):
    p = Politician.objects.get(id=p_id,delete=False)
    k = PoliticianKeywordValue.objects.filter(politician=p, keyword__delete=False)
    return render(request, 'politicians/politician.html',
    {'politician': p,
     'keywords': k,
    })

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_candidates(request):
    p = Politician.objects.filter(candidate_riding__isnull=False)
    return render(request, 'politicians/politicians.html',
        {'politicians': p,
         'type':str("Candidates")
         })

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_incumbents(request):
    p = Politician.objects.filter(incumbent_riding__isnull=False)
    return render(request, 'politicians/politicians.html',
        {'politicians': p,
         'type':str("Incumbents")
         })

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_politicians(request, r_id):
    p = Politician.objects.all()
    return render(request, 'politicians/politicians.html',
        {'politicians': p,
         'type':str("Politicians"),
     'r_id': r_id
    })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def add_politician(request):
    if request.method == 'POST':
        form = Politician_Add_Form(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(add_politician_keyword, args=[Politician.objects.all().count()]))
    else:
        form = Politician_Add_Form()
    return render(request, 'politicians/add_politician.html', { 'form':form})
    
@user_passes_test(define_view_permissions(['EO'],['BEF']))
def add_politician_keyword(request, p_id):
    PoliticianKeywordValueFormSet = formset_factory(addPoliticianKeywordValueForm, extra = 0)
    if request.method == 'POST':
        formset = PoliticianKeywordValueFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                form.save()
            return HttpResponseRedirect(reverse(view_politician, args=[p_id]))
    else:
        data = []
        for i in range(PoliticianKeywordList.objects.all().count()):
            if not PoliticianKeywordList.objects.get(id=i+1).delete:
                data.append({'politician':p_id,'keyword':i+1})
        formset = PoliticianKeywordValueFormSet(initial=data)

    return render(request,'keywords/addpolitician.html',{'formset':formset,'p_id':p_id})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def modify_politician(request, p_id):
    politician = Politician.objects.get(id=p_id)
    if request.method == 'POST':
        form = Politician_Modify_Form(request.POST,instance=politician)
        if form.is_valid():
            form.save()
            if politician.delete:
                return HttpResponseRedirect(reverse(view_all_politicians))
            else:
                return HttpResponseRedirect(reverse(view_politician, args=[p_id]))
    else:
        form = Politician_Modify_Form(instance=politician)
    return render(request, 'politicians/modify_politician.html', { 'form':form, 'politician':politician })
