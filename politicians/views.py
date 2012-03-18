from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ridings.models import Riding
from politicians.models import Politician, PoliticianForm

# TODO Add decorators limiting access

# Candidate/Incumbent Information
# NOTE Should we have one set of functions for incumbents and candidates,
# and just display different info based on a flag?

def view_politician(request, p_id):
    p = Politician.objects.get(id=p_id)
    return render_to_response('politicians/politician.html',{'politician': p})
	
def view_candidates(request):
    p = Politician.objects.filter(candidate_riding__isnull=False)
    return render_to_response('politicians/politicians.html',{'politicians': p,'type':str("Candidates")})

def view_incumbents(request):
    p = Politician.objects.filter(incumbent_riding__isnull=False)
    return render_to_response('politicians/politicians.html',{'politicians': p,'type':str("Incumbents")})

def view_politicians(request):
    p = Politician.objects.all()
    return render_to_response('politicians/politicians.html',{'politicians': p,'type':str("Politicians")})

def add_politician(request):
    if request.method == 'POST':
	form = PoliticianForm(request.POST)
	if form.is_valid():
	    form.save()
	    return HttpResponseRedirect(reverse(view_politicians))
    else:
	form = PoliticianForm()
    return render(request, 'politicians/add_politician.html', 		{ 'form':form,})


