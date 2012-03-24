import urlparse
# Django
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
# django-auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME, logout, authenticate, login as auth_login
from django.contrib.auth.views import login as base_login_view
# django-messages
from django.contrib import messages
# Election
from election.models import Election, RecountForm, ElectionForm

# TODO Add decorators limiting access

# General

@login_required
def index(request):
    """ Display the index page. """
    return render_to_response('index.html', 
        {  })

@login_required
def ro_homepage(request):
    """ Display the index page. """
    return render_to_response('election/ro_homepage.html', 
        {  })

@login_required
def eo_homepage(request):
    """ Display the index page. """
    return render_to_response('election/eo_homepage.html',
        {  })

@login_required
def reporter_homepage(request):
    """ Display the index page. """
    return render_to_response('election/reporter_homepage.html',
        {  })

@login_required
def admin_homepage(request):
    """ Display the index page. """
    return render_to_response('election/admin_homepage.html',
        {  })

# Login Management

@never_cache
def logout_user(request):
    logout(request)
    # TODO display message telling user they're logged out
    return HttpResponseRedirect(reverse(index))

@csrf_protect
@never_cache
def login(request, redirect_field_name=REDIRECT_FIELD_NAME, **kwargs):
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    username = request.POST['username']
    password = request.POST['password']
	# START Block from ipauth.views
    ip = None
    if 'ipauth_meta_key' in kwargs:
        ip = request.META.get(kwargs.pop('ipauth_meta_key'), None)
    if ip is None and hasattr(settings,'IPAUTH_IP_META_KEY'):
        ip = request.META.get(settings.IPAUTH_IP_META_KEY, None)
    if ip is None:
        ip = request.META['REMOTE_ADDR']
	# FIN Block from ipauth.views
    user = authenticate(username=username, password=password, ip=ip)
    if user is None or not user.is_active:
        return base_login_view(request, redirect_field_name=redirect_field_name, 
                               **kwargs)
	auth_login(request, user)
    
	messages.add_message(request, messages.INFO,
                        'You are now logged in as %s on %s' % (user.get_full_name(), ip))
    
    netloc = urlparse.urlparse(redirect_to)[1]
    
    # Use default setting if redirect_to is empty
    if not redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    
    # Security check -- don't allow redirection to a different
    # host.
    elif netloc and netloc != request.get_host():
        redirect_to = settings.LOGIN_REDIRECT_URL
    
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    
    return HttpResponseRedirect(redirect_to)

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
