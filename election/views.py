import urlparse
import json
from itertools import chain
from datetime import date
from droop.election import Election as DroopElection
from droop.profile import ElectionProfile as DroopElectionProfile
from droop.profile import ElectionProfileError as DroopElectionProfileError
# This is our BCSTV rules for Droop
from election.rules import BCSTVRule
# Django
from django.conf import settings
from django.core import management
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
# django-auth
from django.contrib.auth import REDIRECT_FIELD_NAME, logout, authenticate, login as auth_login
from django.contrib.auth.views import login as base_login_view
from django.contrib.auth.decorators import user_passes_test, login_required
# django-messages
from django.contrib import messages
# Election
from election.models import Election, RecountForm, ElectionForm
from election.models import define_view_permissions, permissions_or, permissions_and, permission_always
from ridings.models import Riding, Poll
from ballots.models import Ballot
from django.db.models import Count
from politicians.models import Politician



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
	#TODO: Do something better with this. Should it start a new election?
	else:#archive
		election_action = 'Archive Election'
	return render(request, 'election/admin_homepage.html',{
		'election_action': election_action,
		})

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

######################################
@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_election(request):
	#elec_list = Election.objects.all()
	#elec_list = elec_list[(elec_list.count()-1)]
	# FIXME: undefined variable
	return render(request, 'election/view.html', {'election': (elec_list) })
######################################

@user_passes_test(define_view_permissions(['ADMIN'],['BEF','DUR','AFT','ARC']))
def change_election_status(request):
	election = Election.objects.all()[0]
	errors=election.changeStatus()
	if errors:
		for (k,v) in errors.iteritems():
			messages.error(request, "Riding " + k.name + v)            
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
			return HttpResponseRedirect(reverse(index))
	else:
		form = ElectionForm(instance=election)
	return render(request, 'election/change_election_status.html', {'election':election, 'form' : form})

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
		form = RecountForm()
    
	return render(request, 'election/start_recount.html', {
		'form': form,
		})

@user_passes_test(permissions_or(define_view_permissions(['EO'],['DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def calc_winners(request, r_id):
	r = Riding.objects.get(id=r_id)
	# All ballots for a riding
	all_ballots = r.ballots()
	# All ballots for the calculation
	# TODO: Should this filtering move to the Riding class or Ballot class?
	calculation_ballots = all_ballots.filter(state='C').filter(spoiled=False)
	# All spoiled ballots
	# TODO: Should this filtering move to the Riding class or Ballot class?
	num_spoiled_ballots = r.num_spoiled_ballots()
	# All candidates for the riding
	c = Politician.objects.filter(candidate_riding=r).filter(delete=False)
	# Get distinct ballot contents and how many times they occured
	b2 = calculation_ballots.values("vote").annotate(cnt=Count('vote'))
	# Dictionary of (key=droop candidate ID, value=politician.id)
	c2 = dict((i+1,v.id) for i, v in enumerate(list(c)))
	# Dictionary of (key=politician.id, value=droop candidate ID)
	c2b = dict((v,k) for k,v in c2.iteritems())
	winners = []
	fc_votes = {}
	for politician in c:
		fc_votes[politician.id] = 0


	#check if the number of ballots is enough for BCSTV
	if calculation_ballots.count() < (r.num_candidates() + 1):
		error = "Too few ballots to calculate BCSTV."
		return render(request, 'election/error.html', {'error': error, 'riding': r})

	# Start of BLT generation
	# Number of candidates, Number of seats
	data = str(c.count()) + " " + str(r.num_seats) + "\n"
	# For each distinct ballot content
	for ballot in b2:
		# Count of timesro_home.html
		data = data + str(ballot['cnt']) + " "
		# Content of ballot
		vote_line = json.loads(ballot['vote'])
		first = True
		for _i, _c in vote_line.iteritems():
			# Of the droop ID numbers for the candidate
			if _c == "":
				# If empty, skip (empty line on ballot)
				pass
			else:
				data = data + str(c2b[int(_c)]) + " "
				if first:
					fc_votes[int(_c)] += ballot['cnt']
					first = False

		print fc_votes
		# 0 to say no more candidates on ballot
		data = data + "0\n"
	# 0 to say no more ballots
	data = data + "0\n"

	# candidates in droop order
	for key, candidate in c2.iteritems():
		data = data + "\"" + str(candidate) + "\"\n"
	# Name of election
	data = data + "\"" + r.name + " Results\""
	# End of BLT generation

	try:
		E = DroopElection(DroopElectionProfile(data=data.encode('ascii', 'ignore')), dict(rule='bcstv'))
	except DroopElectionProfileError as e:
		# TODO: catch and send nice page for election
		# "too few ballots" => did not meet droop quota to vote, must be more ballots than candidates
		# "too few candidates" => seats > candidates
		if r.num_seats < 1:
			error = "Too few Seats in " + r.name
		elif r.num_candidates() < r.num_seats:
			error = "Too few Candidates in " + r.name + ". " + str(r.num_seats) + " seats for " + str(r.num_candidates()) + " candidates."
		else:
			error = e
		return render(request, 'election/error.html', {'error': error, 'riding': r})
    

	E.count()
	result = E.record()
	for i in range(len(result['actions'][-1]['cstate'])):
		temp = []
		k = result['cdict'][i+1]['name']
		temp.append(Politician.objects.get(id = k))
		temp.append(result['actions'][-1]['cstate'][i+1])
		temp.append(fc_votes[int(k)])
		winners.append(temp)

	polls = r.poll_range()
    
	return render(request, 'election/winners.html', {
		'riding': r ,
		'candidates': c, 
		'results': result, 
		'numVotes': result['nballots'],
		'numSpoiled': num_spoiled_ballots,
		'winners': winners,
		'polls': polls
		})

@user_passes_test(permissions_or(define_view_permissions(['EO'],['DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def calc_all_winners(request):
	#lists for attributes for each riding

	x = []
	for r in Riding.objects.filter(delete=False):
		# All ballots for a riding
		all_ballots = r.ballots()
		# All ballots for the calculation
		# TODO: Should this filtering move to the Riding class or Ballot class?
		calculation_ballots = all_ballots.filter(state='C').filter(spoiled=False)
		# All spoiled ballots
		# TODO: Should this filtering move to the Riding class or Ballot class?
		num_spoiled_ballots = r.num_spoiled_ballots()
		# All candidates for the riding
		c = Politician.objects.filter(candidate_riding=r).filter(delete=False)
		# Get distinct ballot contents and how many times they occured
		b2 = calculation_ballots.values("vote").annotate(cnt=Count('vote'))
		# Dictionary of (key=droop candidate ID, value=politician.id)
		c2 = dict((i+1,v.id) for i, v in enumerate(list(c)))
		# Dictionary of (key=politician.id, value=droop candidate ID)
		c2b = dict((v,k) for k,v in c2.iteritems())
		polls = r.poll_range()
		# List of all the required Data
		info = []
		winners = []
		fc_votes = {}
		for politician in c:
			fc_votes[politician.id] = 0


		#check if the number of ballots is enough for BCSTV
		if calculation_ballots.count() < (r.num_candidates() + 1):
			error = "Too few ballots to calculate BCSTV."
			return render(request, 'election/error.html', {'error': error, 'riding': r})

		# Start of BLT generation
		# Number of candidates, Number of seats
		data = str(c.count()) + " " + str(r.num_seats) + "\n"
		# For each distinct ballot content
		for ballot in b2:
			# Count of times
			data = data + str(ballot['cnt']) + " "
			# Content of ballot
			vote_line = json.loads(ballot['vote'])
			first = True
			for _i, _c in vote_line.iteritems():
				if _c == "":
					pass
				else:
					# Of the droop ID numbers for the candidate
					data = data + str(c2b[int(_c)]) + " "
					if first:
						fc_votes[int(_c)] += ballot['cnt']
						first = False

			# 0 to say no more candidates on ballot
			data = data + "0\n"
		# 0 to say no more ballots
		data = data + "0\n"

		# candidates in droop order
		for key, candidate in c2.iteritems():
			data = data + "\"" + str(candidate) + "\"\n"
		# Name of election
		data = data + "\"" + r.name + " Results\""
		# End of BLT generation
		try:
			E = DroopElection(DroopElectionProfile(data=data.encode('ascii', 'ignore')), dict(rule='bcstv'))
			E.count()
		except DroopElectionProfileError as e:
			if r.num_seats < 1:
				error = "Too few Seats in " + r.name
			elif r.num_candidates() < r.num_seats:
				error = "Too few Candidates in " + r.name + ". " + str(r.num_seats) + " seats for " + str(r.num_candidates()) + " candidates."
			else:
				error = e
			return render(request, 'election/error.html', {'error': error, 'riding': r})

		result = E.record()

		#places all information in a list

		info.append(r)
		info.append(c)
		info.append(result)
		info.append(result['nballots'])
		info.append(num_spoiled_ballots)

		for i in range(len(result['actions'][-1]['cstate'])):
			temp = []
			k = result['cdict'][i+1]['name']
			temp.append(Politician.objects.get(id = k))
			temp.append(result['actions'][-1]['cstate'][i+1])
			temp.append(fc_votes[int(k)])
			winners.append(temp)

		info.append(winners)
		info.append(polls)
        
		x.append(info)
        
        
	return render(request, 'election/all_winners.html', {
		'results':x
		})

def save_db(request):
    election = Election.objects.all()[0]
    election_action = 'GOTO: Next Election State (Current State:  '+election.status+')'
    if election.status=='BEF':
        election_action = 'Start election'
    elif election.status=='DUR':
        election_action = 'End election'
    elif election.status=='AFT':
        election_action = 'Archive Election'
    #TODO finish this
    messages.info(request, "save DB")
    #management.call_command('flush', verbosity=0, interactive=False)
    #management.call_command('loaddata', 'test_data', verbosity=0)
    return render(request, 'election/admin_homepage.html',{
        'election_action': election_action,
    })

def reset_db(request):
    election = Election.objects.all()[0]
    election_action = 'GOTO: Next Election State (Current State:  '+election.status+')'
    if election.status=='BEF':
        election_action = 'Start election'
    elif election.status=='DUR':
        election_action = 'End election'
    elif election.status=='AFT':
        election_action = 'Archive Election'
    # TODO finish this
    messages.info(request,"reset DB")
    management.call_command('reset', 'ballots', interactive=False)
    print 'reset ballots'
    management.call_command('reset', 'keywords', interactive=False)
    print 'reset keywords'
    management.call_command('reset', 'politicians', interactive=False)
    print 'reset politicians'
    election.status='BEF'
    election.save()
    print "election status reset"
    return render(request, 'election/admin_homepage.html',{
        'election_action': election_action,
    })
    
def reset_db_full(request):
    messages.info(request,"Database completely reset, new election started.  Default user: admin, password: admin")
    management.call_command('flush', interactive=False)
    #TODO change election to current date, election name to <date> election
    election = Election.objects.all()[0]
    election.start = date.today()
    election.description = str(date.today())+" Election"
    election.save()
    return redirect(index)

