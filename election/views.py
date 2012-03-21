from django.shortcuts import render_to_response  
from election.models import Election

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
    return render_to_response('election/reporter_homepage.html.html', 
        {  })

def admin_homepage(request):
    """ Display the index page. """
    return render_to_response('election/admin_homepage.html.html', 
        {  })


# Election Management

def view_election(request):
   elec_list = Election.objects.all()
   return render_to_response('election/view.html', {'election':elec_list})

