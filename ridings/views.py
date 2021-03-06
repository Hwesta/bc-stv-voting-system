from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from ridings.models import Riding, Poll, Riding_Add_Form, Riding_Modify_Form, Poll_Add_Form, Poll_Modify_Form, ChooseRidingForm
from ballots.models import Ballot
from politicians.models import Politician
from keywords.models import RidingKeywordValue, RidingKeywordList, PoliticianKeywordValue, addRidingKeywordValueForm
from django.contrib.auth.decorators import user_passes_test
from election.models import define_view_permissions, permissions_or, permissions_and, permission_always
from django.contrib import messages

# TODO Add decorators limiting access

# Riding Information
@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_all_ridings(request):
    #""" View list of all the ridings. """
    # exlude deleted ridings from list
    ridings = Riding.objects.filter(delete=False)
    # render page
    return render(request, 'ridings/ridings.html',{
        'ridings': ridings,
        'type': str('ridings')
        })

@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','DUR','AFT']), define_view_permissions(['REP'],['DUR'])))
def view_riding(request, r_id):
    #""" View all the details about a riding on one page. """
    # store all necessary information for a riding into variables to be added to the dictionary
    riding = Riding.objects.get(id=r_id)
    polls = riding.poll_range()
    incumbents = riding.incumbents().filter(delete=False)
    candidates =riding.candidates().filter(delete=False)
    keywords = RidingKeywordValue.objects.filter(riding=riding, keyword__delete=False)
    #these two lines give confirmed and distinct unverified # of ballots
    ballots = riding.ballots().filter(state='C').count()
    ballots = ballots + riding.ballots().filter(state='U').values('ballot_num').distinct().count()
    spoiled = riding.num_spoiled_ballots()
    # render page
    return render(request, 'ridings/riding.html', {
        'riding': riding,
        'polls': polls,
        'candidates': candidates,
        'incumbents': incumbents,
        'keywords': keywords,
        'ballots': ballots,
        'spoiled': spoiled,
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
            return HttpResponseRedirect(reverse(view_riding, args=[r_id]))
    else:
        data = []
        for kw in RidingKeywordList.objects.filter(delete=False):
            data.append({'riding':r_id, 'keyword':kw.id})
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
            if riding.delete == True:
                # Remove now deleted riding from candidates and incumbents
                # If they're no longer a candidate/incumbent, delete them
                incumbents = riding.incumbents()
                for i in incumbents.filter(candidate_riding=None):
                    i.delete=True
                    i.save()
                incumbents.update(incumbent_riding=None)
                        
                # Remove riding from candidates, delete candidates that are not also incumbents
                candidates = riding.candidates()
                for c in candidates.filter(incumbent_riding=None):
                    c.delete=True
                    c.save()
                candidates.update(candidate_riding=None)
                return HttpResponseRedirect(reverse(view_all_ridings))
            else:
                return HttpResponseRedirect(reverse(view_riding, args=(r_id,)))
    else:
        form = Riding_Modify_Form(instance=riding)
    return render(request, 'ridings/modify_riding.html', {'form': form, 'riding': riding, })


# Poll Management

# all poll functions follow the same logic as riding functions
# Only Admin can access polls during an election.
# The number of open polls remaining can be calculated by the poll range - ( deleted polls + closed polls ) 
@user_passes_test(permissions_or(define_view_permissions(['EO'],['BEF','AFT']), define_view_permissions(['ADMIN'],['DUR'])))
def view_polls(request, riding_id):
    riding = Riding.objects.get(id=riding_id)
    p = Poll.objects.filter(riding=riding).exclude(delete=True)
    return render(request, 'ridings/polls.html', {
        'polls': p,
        'type': str('Polls'),
        'riding': riding,
        })

# modified start_recount that just passes a riding id to view_polls
@user_passes_test(define_view_permissions(['ADMIN'],['DUR']))
def choose_riding(request):
    if request.method == 'POST': 
        form = ChooseRidingForm(request.POST) 
        if form.is_valid():
            riding = form.cleaned_data['riding']
            return HttpResponseRedirect(reverse(view_polls, args=(riding.id,)))
    else:
        form = ChooseRidingForm()

    return render(request, 'ridings/choose_riding.html', {
        'form': form,
        })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def add_poll(request, riding_id):
    riding = Riding.objects.get(id=riding_id)
    if request.method == 'POST':
        form = Poll_Add_Form(request.POST)
        if form.is_valid():
            new_poll = form.save(commit=False)
            new_poll.riding = riding
            new_poll.save()
            return HttpResponseRedirect(reverse(view_polls, args=(riding_id,)))
    else:
        form = Poll_Add_Form()
    return render(request, 'ridings/add_poll.html', {
        'form': form,
        'riding': riding,
        })

@user_passes_test(define_view_permissions(['EO'],['BEF']))
def modify_poll(request, riding_id, poll_id):
    riding = Riding.objects.get(id=riding_id)
    poll = Poll.objects.get(id=poll_id, riding=riding)
    if request.method == 'POST':
        form = Poll_Modify_Form(request.POST, instance=poll)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(view_polls, args=(riding_id,)))
    else:
        form = Poll_Modify_Form(instance=poll)
    return render(request, 'ridings/modify_poll.html', {
        'form': form,
        'poll': poll,
        'riding': riding,
        })

@user_passes_test(define_view_permissions(['ADMIN'],['DUR']))
def close_poll(request, riding_id, poll_id):
    poll = Poll.objects.get(id=poll_id)
    # # of ballots belonging to the poll that are unverified
    num_u_ballots = Ballot.objects.filter(poll=poll_id, state='U').count()
    if num_u_ballots == 0:
    #if poll.riding.safe_to_close():
        poll.close()
    else:
        messages.error(request, "Poll can't be closed as unverified ballots remain.")
    return HttpResponseRedirect(reverse(view_polls, args=(riding_id,)))
