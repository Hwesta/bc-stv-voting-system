import urlparse
import json
from itertools import chain
from droop.election import Election as DroopElection
from droop.profile import ElectionProfile as DroopElectionProfile
# This is our BCSTV rules for Droop
from election.rules import BCSTVRule
# Django
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.shortcuts import render
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
from ridings.models import Riding, Poll
from ballots.models import Ballot
from django.db.models import Count
from politicians.models import Politician



# TODO Add decorators limiting access

# General

@login_required
def index(request):
    """ Display the index page. """
    return render(request, 'index.html', 
        {  })

@login_required
def ro_homepage(request):
    """ Display the index page. """
    return render(request, 'election/ro_homepage.html', 
        {  })

@login_required
def eo_homepage(request):
    """ Display the index page. """
    return render(request, 'election/eo_homepage.html',
        {  })

@login_required
def reporter_homepage(request):
    """ Display the index page. """
    return render(request, 'election/reporter_homepage.html',
        {  })

@login_required
def admin_homepage(request):
    """ Display the index page. """
    return render(request, 'election/admin_homepage.html',
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
   elec_list = elec_list[(elec_list.count()-1)]
   return render(request, 'election/view.html', {'election': (elec_list) })

def change_election_status(request):
   elec_list = Election.objects.all()
   elec_list = elec_list[(elec_list.count()-1)]
   if request.method == 'POST':
       form = ElectionForm(request.POST)
       if form.is_valid():
           form.save()
           return HttpResponseRedirect(reverse(index))
   else:
       form = ElectionForm()
   return render(request, 'election/change_election_status.html', {'election':elec_list, 'form' : form})

def set_location(request):
   return render(request, 'election/set_location.html', {})

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

def calc_winners(request, r_id):
    r = Riding.objects.get(id=r_id)
    # All ballots for a riding
    all_ballots = r.ballots()
    # All ballots for the calculation
    # TODO: Should this filtering move to the Riding class or Ballot class?
    calculation_ballots = all_ballots.filter(valid=True).filter(verified=True).filter(spoiled=False)
    # All spoiled ballots
    # TODO: Should this filtering move to the Riding class or Ballot class?
    spoiled_ballots = all_ballots.filter(verified=True).filter(spoiled=True)
    # All candidates for the riding
    c = Politician.objects.filter(candidate_riding=r)
    # Get distinct ballot contents and how many times they occured
    b2 = calculation_ballots.values("vote").annotate(cnt=Count('vote'))
    # Dictionary of (key=droop candidate ID, value=politician.id)
    c2 = dict((i+1,v.id) for i, v in enumerate(list(c)))
    # Dictionary of (key=politician.id, value=droop candidate ID)
    c2b = dict((v,k) for k,v in c2.iteritems())
    # Debug
    print c
    print c2
    print c2b
    # Start of BLT generation
    # Number of candidates, Number of seats
    data = str(c.count()) + " " + str(r.num_seats) + "\n"
    # For each distinct ballot content
    for ballot in b2:
        # Count of times
        data = data + str(ballot['cnt']) + " "
        # Content of ballot
        vote_line = json.loads(ballot['vote'])
        for _i, _c in vote_line.iteritems():
            # Of the droop ID numbers for the candidate
            data = data + str(c2b[int(_c)]) + " "
        # 0 to say no more candidates on ballot
        data = data + "0\n"
    # 0 to say no more ballots
    data = data + "0\n"

    # candidates in droop order
    for key, candidate in c2.iteritems():
        data = data + "\"k" + str(key) + "\"\n"
    # Name of election
    data = data + "\"" + r.name + " Results\""
    # End of BLT generation

    print "===== BLT"
    print data
    print "====="
    E = DroopElection(DroopElectionProfile(data=data.encode('ascii', 'ignore')), dict(rule='bcstv'))
    E.count()
    print E.report()
    result = E.record()
    return render(request, 'election/winners.html', {
        'riding': r ,
        'candidates': c, 
        'results': result, 
        'numVotes': result['nballots'],
        'numSpoiled': spoiled_ballots.count(),
		'winners': result['actions'][-1]['cstate']
        })
