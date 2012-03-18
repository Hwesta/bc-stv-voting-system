from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ridings.models import Riding, Poll
from ballots.models import Ballot, BallotForm

# Entering Ballots
# TODO Add decorators limiting access

def select_poll():
    """ Enter the poll number to enter/verify ballots for."""
    pass

def enter_ballot():
    """ Enter a ballot information. """
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

def input_ballot(request):
    if request.method == 'POST':
        form = BallotForm(request.POST)
        if form.is_valid():
            new_ballot = form.save()
            return HttpResponseRedirect(reverse(view_ballots))
    else:
        form = BallotForm()

    return render(request, 'ballots/add.html', {'form':form})
