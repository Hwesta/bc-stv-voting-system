from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count
from ridings.models import Riding, Poll
from ballots.models import Ballot, BallotForm

# Entering Ballots
# TODO Add decorators limiting access

def select_poll():
    """ Enter the poll number to enter/verify ballots for."""
    pass

def verify_ballot():
    """ Display the screen to verify a ballot. """
    pass

def close_poll():
    """ Close the poll and check all inputted ballots.

    Should be called once all ballots for a poll are entered.  Check if the
    ballots have been entered twice, and if so compare the results, generating
    a list of ballots that need ot be verified.
    """
    pass

def view_ballots(request):
    ballot_list = Ballot.objects.all()
    return render_to_response('ballots/view.html', {'ballots':ballot_list})

def view_ballot(request, b_id):
    ballot = Ballot.objects.get(id=b_id)
    return render_to_response('ballots/view_single.html', {'ballot':ballot, 'ballot_num':b_id})

def input_ballot(request):
    if request.method == 'POST':
        form = BallotForm(request.POST)
        if form.is_valid():
            new_ballot = form.save()
            return HttpResponseRedirect(reverse(view_ballots))
    else:
        form = BallotForm()

    return render(request, 'ballots/add.html', {'form':form})

def view_conflict_list(request):
    auto_ballots = Ballot.objects.filter(verified=False).values('ballot_num','vote').annotate(cnt=Count('ballot_num')).filter(cnt__gt=1)
    for b in auto_ballots:
        ballots = Ballot.objects.filter(ballot_num=b['ballot_num'])
        for ballot in ballots:
            ballot.verified = True
            ballot.save()
    manual_ballots = Ballot.objects.filter(verified=False).values('ballot_num','vote').annotate(cnt=Count('ballot_num')).values('ballot_num').annotate(cnt=Count('ballot_num'))
    ballots = {}
    for b in manual_ballots:
        if b['ballot_num'] not in ballots:
            ballots[b['ballot_num']] = []
        ballots[b['ballot_num']].append(Ballot.objects.filter(ballot_num=b['ballot_num']))
    return render_to_response('ballots/view_conflicts.html', {'ballots':ballots, 'ballot_nums':ballots.keys()})
