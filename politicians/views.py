from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ridings.models import Riding
from politicians.models import Politician, PoliticianForm
from keywords.models import PoliticianKeywordValue, PoliticianKeywordList

# TODO Add decorators limiting access

# Candidate/Incumbent Information
# NOTE Should we have one set of functions for incumbents and candidates,
# and just display different info based on a flag?

def view_politician(request, r_id, p_id):
    p = Politician.objects.get(id=p_id)
    k = PoliticianKeywordValue.objects.filter(politician=p)
    return render(request, 'politicians/politician.html',
	{'politician': p,
	 'keywords': k,
	 'r_id': r_id
	})

def view_candidates(request):
    p = Politician.objects.filter(candidate_riding__isnull=False)
    return render(request, 'politicians/politicians.html',
        {'politicians': p,
         'type':str("Candidates")
         })

def view_incumbents(request):
    p = Politician.objects.filter(incumbent_riding__isnull=False)
    return render(request, 'politicians/politicians.html',
        {'politicians': p,
         'type':str("Incumbents")
         })

def view_politicians(request, r_id):
    p = Politician.objects.all()
    return render(request, 'politicians/politicians.html',
        {'politicians': p,
         'type':str("Politicians"),
	 'r_id': r_id
	})

def view_deleted_politicians(request, r_id):
    p = Politician.objects.all()
    return render(request, 'politicians/deleted_politicians.html',
        {'politicians': p,
         'type':str("Deleted Politicians"),
	 'r_id': r_id
         })

def add_politician(request, r_id):
    if request.method == 'POST':
        form = PoliticianForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(view_politicians, args=(r_id)))
    else:
        form = PoliticianForm()
    return render(request, 'politicians/add_politician.html', { 'form':form, 'r_id': r_id})

def modify_politician(request, r_id, p_id):
    politician = Politician.objects.get(id=p_id)
    if request.method == 'POST':
        form = PoliticianForm(request.POST,instance=politician)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(view_politicians, args=(r_id)))
    else:
        form = PoliticianForm(instance=politician)
    return render(request, 'politicians/modify_politician.html', { 'form':form, 'politician':politician, 'r_id': r_id})


