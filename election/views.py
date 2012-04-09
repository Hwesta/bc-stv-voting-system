import urlparse
import json
import zipfile
from itertools import chain
from datetime import date
# Django
from django.conf import settings
from django.core import management
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
# django-auth
from django.contrib.auth import REDIRECT_FIELD_NAME, logout, authenticate, login as auth_login
from django.contrib.auth.views import login as base_login_view
from django.contrib.auth.decorators import user_passes_test, login_required
# django-messages
from django.contrib import messages
# Droop
from droop.profile import ElectionProfileError as DroopElectionProfileError
# Election
from election.models import Election, RecountForm, ElectionForm
from election.models import define_view_permissions, permissions_or, permissions_and, permission_always
from ridings.models import Riding, Poll
from ballots.models import Ballot
from django.db.models import Count
from politicians.models import Politician
from keywords.models import PoliticianKeywordList, PoliticianKeywordValue

# General

@login_required
@user_passes_test(permission_always)
def index(request):
    #""" Display the index page. """
    user_groups = request.user.groups.all()
    if user_groups.count() == 0:
        return render(request, 'index.html')
    elif user_groups[0].name == 'RO':
        return redirect(ro_homepage)
    elif user_groups[0].name == 'EO':
        return redirect(eo_homepage)
    elif user_groups[0].name == 'REP':
        return redirect(reporter_homepage)
    elif user_groups[0].name == 'ADMIN':
        return redirect(admin_homepage)
    else:
        return render(request, 'index.html')

@login_required
@user_passes_test(define_view_permissions(['RO'],['BEF','DUR','AFT']))
def ro_homepage(request):
    #""" Display the index page. """
    return render(request, 'election/ro_homepage.html')

@login_required
@user_passes_test(define_view_permissions(['EO'],['BEF','DUR','AFT']))
def eo_homepage(request):
    #""" Display the index page. """
    return render(request, 'election/eo_homepage.html')

@login_required
@user_passes_test(define_view_permissions(['REP'],['BEF','DUR','AFT']))
def reporter_homepage(request):
    #""" Display the index page. """
    return render(request, 'election/reporter_homepage.html')

@login_required
@user_passes_test(define_view_permissions(['ADMIN'],['BEF','DUR','AFT','ARC']))
def admin_homepage(request):
    #""" Display the index page. """
    election = Election.objects.all()[0]
    election_action = 'GOTO: Next Election State (Current State:  '+election.status+')'
    if election.status=='BEF':
        election_action = 'Start election'
    elif election.status=='DUR':
        election_action = 'End election'
    elif election.status=='AFT':
        election_action = 'Archive Election'
    return render(request, 'election/admin_homepage.html',{
        'election_action': election_action,
        })

# Login Management

@never_cache
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
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

    messages.add_message(request, messages.INFO, 'You are now logged in as %s on %s' % (user.get_full_name(), ip))

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

@user_passes_test(define_view_permissions(['ADMIN'],['BEF','DUR','AFT','ARC']))
def change_election_status(request):
    election = Election.objects.all()[0]
    (riding_errors, errors)=election.change_status()
    if errors or riding_errors:
        for (k,v) in riding_errors.iteritems():
            for i in v:
                messages.error(request, "Riding " + k.name + i)
        for v in errors:
            messages.error(request, v)            
        return HttpResponseRedirect(reverse('election.views.admin_homepage'))
    else:
        election.save()
        messages.success(request, "Election state changed to: "+election.get_status_display())
        return HttpResponseRedirect(reverse('election.views.admin_homepage'))


@user_passes_test(define_view_permissions(['ADMIN'],['BEF']))
def change_election(request):
    ##if status isn't initiated yet it can't be used
    #election = Election.objects.exclude(status='ARC').all()
    election = Election.objects.all()
    # TODO: This will only work with one election for now
    if len(election) == 0:
        election = Election()
        election.save()
    else:
        election = election[0]
   
    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            form.save()
            messages.success(request, "Election information successfully updated.")
            return HttpResponseRedirect(reverse(index))
    else:
        form = ElectionForm(instance=election)
    return render(request, 'election/change_election.html', {'election':election, 'form' : form})

@user_passes_test(define_view_permissions(['ADMIN'],['BEF']))
def set_location(request):
    return render(request, 'election/set_location.html', {})

@user_passes_test(define_view_permissions(['ADMIN'],['DUR','AFT']))
def start_recount(request):
    if request.method == 'POST': 
        form = RecountForm(request.POST) 
        if form.is_valid():
            riding = form.cleaned_data['riding']
            riding.active = True
            riding.recount_needed = False
            riding.save()
            polls = riding.poll_set.exclude(delete=True)

            for poll in polls:
                poll.active = True
                poll.save()

            ballots = riding.ballots()
            for ballot in ballots:
                ballot.state = 'R'
                ballot.save()
            messages.success(request, "Recount started for riding "+riding.name+".")
            return HttpResponseRedirect(reverse(index))
        else:
            messages.error(request, "You must select a riding.")
    form = RecountForm()
        
    return render(request, 'election/start_recount.html', {
        'form': form,
        })

@user_passes_test(permissions_or(define_view_permissions(['EO'],['DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def calc_winners(request, r_id):
    r = Riding.objects.get(id=r_id)
    E = winners = result = candidates = None

    try:
        _ = r.calc_winners()
        E = _['E']
        candidate_states = _['candidate_states']
        result = _['result']
        candidates = _['candidates']
        num_spoiled_ballots = _['num_spoiled_ballots']
    except DroopElectionProfileError as e:
            # TODO: catch and send nice page for election
            # "too few ballots" => did not meet droop quota to vote, must be more ballots than candidates
            # "too few candidates" => seats > candidates
            return render(request, 'election/error_riding.html', {'error': e, 'riding': r})

    polls = r.poll_range()

    dump = E.dump()
    dumphtml = []
    dumphtmlhead = []
    for i,l in enumerate(dump.split("\n")):
        l = l.split("\t")
        if i == 0:
            dumphtmlhead = l
        else:
            dumphtml.append(l)
    
    return render(request, 'election/winners.html', {
        'riding': r ,
        'candidates': candidates, 
        'results': result, 
        'numVotes': result['nballots'],
        'numSpoiled': num_spoiled_ballots,
        'candidate_states': candidate_states,
        'dumphtml': dumphtml,
        'dumphtmlhead': dumphtmlhead,
        })

@user_passes_test(permissions_or(define_view_permissions(['EO'],['DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def calc_all_winners(request):
    #lists for attributes for each riding

    results = []
    for r in Riding.objects.filter(delete=False):
        try:
            result = r.calc_winners()
            results.append(result)
        except DroopElectionProfileError as e:
            messages.error(request, e)
        
    return render(request, 'election/all_winners.html', {
        'results': results
        })

def save_db(request):
    # These are inside the function because they are quite large, and we want to
    # keep them in local scope, not global
    from StringIO import StringIO
    from settings import TABLE_DUMP_ORDER

    # Generate the dumpdata and save as strings in exports
    exports = []
    for tl in TABLE_DUMP_ORDER:
        buf = StringIO()
        management.call_command('dumpdata', *tl, verbosity=1, indent=2, format='json', stdout=buf)
        buf.seek(0)
        exports.append(buf.read())
    # exports now contains each of the JSON blobs to import, in THAT exact order.

    # from https://code.djangoproject.com/wiki/CookBookDynamicZip
    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'filename=election.zip'
    #now add them to a zip file. note the zip only exist in memory as you add to it
    buffer = StringIO()
    electionzip = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    for index, election_data in enumerate(exports):
        electionzip.writestr("election_data_%03d.json" % (index,), election_data)
    electionzip.close()
    buffer.flush()
    #the import detail--we return the content of the buffer
    ret_zip = buffer.getvalue()
    buffer.close()
    response.write(ret_zip)
    return response

def reset_db(request):
    messages.success(request, "Ballots, incumbents, candidates, and associated keywords have been deleted.  New election has been started.")
    Ballot.objects.all().delete()
    PoliticianKeywordValue.objects.all().delete()
    PoliticianKeywordList.objects.all().delete()
    Politician.objects.all().delete()
    # TODO change all winning candidates to incumbents
    
    election = Election.objects.all()[0]
    election.start = date.today()
    election.description = str(date.today())+" Election"
    election.status = 'BEF'
    election.save()
    return redirect(admin_homepage)
    
def reset_db_full(request):
    messages.success(request,"Database completely reset, new election started.  Default user: admin, password: admin")
    management.call_command('flush', interactive=False)

    election = Election.objects.all()[0]
    election.start = date.today()
    election.description = str(date.today())+" Election"
    election.status = 'BEF'
    election.save()
    return redirect(index)

