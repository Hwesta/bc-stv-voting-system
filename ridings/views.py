from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from ridings.models import Riding, Poll, Riding_Add_Form, Riding_Modify_Form, PollForm
from politicians.models import Politician
from keywords.models import RidingKeywordValue, RidingKeywordList, PoliticianKeywordValue, addRidingKeywordValueForm
from django.contrib.auth.decorators import user_passes_test
from election.models import define_view_permissions, permissions_or, permissions_and
from election.views import get_status_display

# TODO Add decorators limiting access

# Riding Information
@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_all_ridings(request):
    #""" View list of all the ridings. """
    # exlude deleted ridings from list
    ridings = Riding.objects.filter(delete=False)
    elec = get_status_display(request)
    # render page
    return render(request, 'ridings/ridings.html',{
		'ridings': ridings,
        'election': elec,
		'type': str('ridings')
		})

@user_passes_test(define_view_permissions(['EO'],['BEF','DUR','AFT']))
def view_deleted_ridings(request):
    #""" View list of deleted ridings. """
    # exclude ridings from above function
    ridings = Riding.objects.filter(delete=True)
    # render page
    return render(request, 'ridings/deleted_ridings.html',{'ridings': ridings, 'type': str('ridings')})

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_riding(request, r_id):
    #""" View all the details about a riding on one page. """
    # store all necessary information for a riding into variables to be added to the dictionary
    riding = Riding.objects.get(id=r_id)
    polls = riding.polls()
    incumbents = riding.incumbents().filter(delete=False)
    candidates =riding.candidates().filter(delete=False)
    keywords = RidingKeywordValue.objects.filter(riding=riding)
    # render page
    return render(request, 'ridings/riding.html',
        {'riding': riding,
         'polls': polls,
         'candidates': candidates,
         'incumbents': incumbents,
         'keywords': keywords,
        })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def add_riding(request):
    # """ Adds a new riding to the system. """
    # if submitting the form
    if request.method == 'POST':
	# form variable is updated
        form = Riding_Add_Form(request.POST)
	# input validation
        if form.is_valid():
	    # save information to database
            form.save()
	    # go add riding keywords
            return HttpResponseRedirect(reverse(add_riding_keyword, args=[Riding.objects.all().count()]))
    else:
	# create a blank form instance
        form = Riding_Add_Form()
	# render page
	return render(request, 'ridings/add_riding.html', {'form': form, })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def add_riding_keyword(request, r_id):
    RidingKeywordValueFormSet = formset_factory(addRidingKeywordValueForm, extra=0)
    if request.method == 'POST':
        formset = RidingKeywordValueFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                form.save()
            return HttpResponseRedirect(reverse(view_all_ridings))
    else:
        data = []
        for i in range(RidingKeywordList.objects.all().count()):
            data.append({'riding':r_id,'keyword':i+1})
        formset = RidingKeywordValueFormSet(initial=data)

    return render(request,'keywords/addriding.html',{'formset':formset,'id':r_id})

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def modify_riding(request, r_id):
    #""" Modify existing riding. """
    # identical to above function except the information of the selected riding is added to the form.
    riding = Riding.objects.get(id=r_id)
    if request.method == 'POST':
        form = Riding_Modify_Form(request.POST, instance=riding)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(view_riding, args=(r_id,)))
    else:
        form = Riding_Modify_Form(instance=riding)
	return render(request, 'ridings/modify_riding.html', {'form': form, 'riding': riding, })


# Poll Management

# all poll functions follow the same logic as riding functions
@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_polls(request, riding_id):
    riding = Riding.objects.get(id=riding_id)
    p = Poll.objects.filter(riding=riding)
    return render(request, 'ridings/polls.html',
        {'polls': p,
         'type': str('Polls'),
         'riding': riding,
        })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def add_poll(request, riding_id):
    riding = Riding.objects.get(id=riding_id)
    if request.method == 'POST':
        form = PollForm(request.POST)
        if form.is_valid():
            new_poll = form.save(commit=False)
            new_poll.riding = riding
            new_poll.save()
            return HttpResponseRedirect(reverse(view_polls, args=(riding_id,)))
    else:
        form = PollForm()
    return render(request, 'ridings/add_poll.html',
        {'form': form,
         'riding': riding,
        })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def modify_poll(request, riding_id, poll_id):
    riding = Riding.objects.get(id=riding_id)
    poll = Poll.objects.get(id=poll_id, riding=riding)
    if request.method == 'POST':
        form = PollForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(view_polls, args=(riding_id,)))
    else:
        form = PollForm(instance=poll)
    return render(request, 'ridings/modify_poll.html',
        {'form': form,
         'poll': poll,
         'riding': riding,
        })
