from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count
from ridings.models import Riding, Poll
from ballots.models import Ballot, BallotForm, ChoosePollForm, ChooseRidingToVerifyForm, AcceptBallotForm, LockedBallotForm
from politicians.models import Politician
from election.models import define_view_permissions, permissions_or, permissions_and, permission_always
from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.contrib import messages

# Entering Ballots
@user_passes_test(define_view_permissions(['RO'],['DUR']))
def choose_poll(request):
    """ Enter the poll number to enter ballots for."""
    if request.method == 'POST':
        form = ChoosePollForm(request.POST)
        if form.is_valid():
            poll = form.cleaned_data['poll']
            return HttpResponseRedirect(reverse(input_ballot, args=(poll.id,)))
    else:
        form = ChoosePollForm()

    return render(request, 'ballots/choose_poll.html',
        {'form': form,
        })
    
@user_passes_test(define_view_permissions(['RO'],['DUR']))
def compare_ballot(request, b_id):
    ballot = Ballot.objects.get(id=b_id)
    candidates = Politician.objects.filter(candidate_riding=ballot.poll.riding)
    ballot_list = Ballot.objects.filter(ballot_num=ballot.ballot_num)
    tiebreaker_form = LockedBallotForm(initial={'poll': ballot.poll.id, 'ballot_num': ballot.ballot_num, 'vote': 'invalid'})
    return render(request, 'ballots/compare.html', {
        'ballots':ballot_list,
        'candidates':candidates,
        'tiebreaker_form': tiebreaker_form,
        })

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def auto_accept_ballot(request, ballot_id):
    correct_ballot = Ballot.objects.get(id=ballot_id)
    ballot_num = correct_ballot.ballot_num
    correct_ballot.state='C'
    riding_id = correct_ballot.poll.riding.id
    try:
        correct_ballot.save(current_ro=request.user)
    except IntegrityError as e:
        messages.error(request, str(e))
        return verify_riding(request, riding_id)

    # We don't need the current_ro check here, it was done by the correct_ballot.save()
    for b in Ballot.objects.exclude(state='R').exclude(id=correct_ballot.id).filter(ballot_num=ballot_num).all():
        b.state='I'
        b.save()
    #b=ballot.object(form.ballot)

    messages.info(request, "Auto-Accepted Ballot #%s (id=%s)" % (ballot_num, correct_ballot.id))
    return verify_riding(request, riding_id)

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def accept_ballot(request):
    riding_id = -1
    if request.method == 'POST':
        form = AcceptBallotForm(request.POST)
        #print form.cleaned_data
        if form.is_valid():
            correct_ballot = form.cleaned_data['ballot']
            #print "Saving ballot", correct_ballot
            ballot_num = correct_ballot.ballot_num
            correct_ballot.state='C'
            riding_id = correct_ballot.poll.riding.id
            try:
                correct_ballot.save(current_ro=request.user)
            except IntegrityError as e:
                messages.error(request, str(e))
                return verify_riding(request, riding_id)                
            # We don't need the current_ro check here, it was done by the correct_ballot.save()
            for b in Ballot.objects.exclude(state='R').exclude(id=correct_ballot.id).filter(ballot_num=ballot_num).all():
                b.state='I'
                b.save()
            #b=ballot.object(form.ballot)
            messages.info(request, "Manually Accepted Ballot #%s (id=%s)" % (ballot_num, correct_ballot.id))
            return verify_riding(request, riding_id)

    if riding_id > 0:
        return HttpResponseRedirect(reverse(verify_riding, args=(riding_id,)))
    else:
        return HttpResponseRedirect(reverse(choose_riding_to_verify, args=()))
        

def close_poll():
    """ Close the poll and check all inputted ballots.

    Should be called once all ballots for a poll are entered.  Check if the
    ballots have been entered twice, and if so compare the results, generating
    a list of ballots that need ot be verified.
    """
    # TODO: write me
    pass

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def view_ballots(request):
    ballot_list = Ballot.objects.all()
    return render(request, 'ballots/view.html', {'ballots':ballot_list})

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def view_ballot(request, b_id):
    ballot = Ballot.objects.get(id=b_id)
    return render(request, 'ballots/view_single.html', {'ballot':ballot, 'ballot_num':b_id})

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def input_ballot(request, poll_id, *args, **kwargs):
    poll = Poll.objects.get(id=poll_id)
    candidates = Politician.objects.filter(candidate_riding=poll.riding).filter(delete=False)
        
    if request.method == 'POST':
        form = BallotForm(request.POST)
        if form.is_valid():
            new_ballot = form.save(commit=False)
            new_ballot.entered_by = request.user

            modified_request=request
            modified_request.method="GET"

            riding_id = new_ballot.poll.riding.id
            try:
                new_ballot.save(current_ro=request.user)
            except IntegrityError as e:
                messages.error(request, str(e))
                return input_ballot(modified_request, poll_id)  
            
            messages.success(request, 'Ballot input successful. <a href="/">Done?</a>')
            #return HttpResponseRedirect(reverse(input_ballot, args=(poll.id,)))
            return input_ballot(modified_request, poll_id)
    else:
        form = BallotForm(initial={'poll': poll_id, 'vote': 'invalid'})
    return render(request, 'ballots/add.html', {
                'form':form,
                'candidates':candidates,
            })

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def input_ballot_tiebreaker(request, old_ballot_num):
    # Get old ballots that are not for a recount
    old_ballots = Ballot.objects.exclude(state='R').filter(ballot_num=old_ballot_num).all()
    poll = old_ballots[0].poll
    candidates = Politician.objects.filter(candidate_riding=poll.riding).filter(delete=False)
    if request.method == 'POST':
        form = LockedBallotForm(request.POST,initial={'poll': poll, 'ballot_num': old_ballot_num})
        if form.is_valid():
            # Invalidate old ballots
            for b in old_ballots:
                b.state='I'
                b.save()
            # Save new ballot
            new_ballot = form.save(commit=False)
            new_ballot.entered_by = request.user
            new_ballot.state='C'
            try:
                new_ballot.save(current_ro=request.user)
            except IntegrityError as e:
                messages.error(request, str(e))
                # FIXME: Undefined variables: modified_request, poll_id
                return input_ballot(modified_request, poll_id)
            messages.success(request, "Added tie-break ballot for ballot number "+old_ballot_num)
            #return verify_riding(request, poll.riding.id)
            #return HttpResponseRedirect(reverse(verify_riding, args=(poll.riding.id,)))
        else:
            messages.error(request, "Failed to add tie-break ballot for ballot number "+old_ballot_num)
    else:
        messages.error(request, "Invalid tie-break request for ballot number "+old_ballot_num)
    return verify_riding(request, poll.riding.id)

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def choose_riding_to_verify(request):
    """ Enter the riding to verify ballots for."""
    if request.method == 'POST':
        form = ChooseRidingToVerifyForm(request.POST)
        if form.is_valid():
            riding = form.cleaned_data['riding']
            return HttpResponseRedirect(reverse(verify_riding, args=(riding.id,)))
    else:
        form = ChooseRidingToVerifyForm()

    return render(request, 'ballots/choose_riding_to_verify.html',
        {'form': form,
        })

@user_passes_test(define_view_permissions(['RO'],['DUR']))
def verify_riding(request, riding_id, *args, **kwargs):
    riding = Riding.objects.get(id=riding_id)
    verify_results = riding.verify()

    return render(request, 'ballots/view_conflicts.html', verify_results)
