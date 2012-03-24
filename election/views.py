from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from election.models import Election, RecountForm, ElectionForm

# TODO Add decorators limiting access

# General

def index(request):
    """ Display the index page. """
    return render_to_response('index.html', 
        {  })

def ro_homepage(request):
    """ Display the index page. """
    return render_to_response('election/ro_homepage.html', 
        {  })

def eo_homepage(request):
    """ Display the index page. """
    return render_to_response('election/eo_homepage.html',
        {  })

def reporter_homepage(request):
    """ Display the index page. """
    return render_to_response('election/reporter_homepage.html',
        {  })

def admin_homepage(request):
    """ Display the index page. """
    return render_to_response('election/admin_homepage.html',
        {  })


# Election Management

def view_election(request):
   elec_list = Election.objects.all()
   return render_to_response('election/view.html', {'election':elec_list})

def change_election_status(request):
   elec_list = Election.objects.all()
   if request.method == 'POST':
       form = ElectionForm(request.Post,instance = elec_list)
       if form.is_valid():
           form.save()
           return HttpResponseRedirect(reverse(admin_home))
   else:
       form = ElectionForm()
   return render_to_response('election/change_election_status.html', {'election':elec_list})

def set_location(request):
   return render_to_response('election/set_location.html', {})

def start_recount(request):
    # TODO Add message in redirect saying recount has been started.
    if request.method == 'POST': 
        form = RecountForm(request.POST) 
        if form.is_valid():
            riding = form.cleaned_data['riding']
            riding.active = True
            riding.save()
            return HttpResponseRedirect(reverse(index))
    else:
        form = RecountForm()

    return render(request, 'election/start_recount.html',
        {'form': form,
        })
