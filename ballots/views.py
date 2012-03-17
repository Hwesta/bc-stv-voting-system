from django.shortcuts import render_to_response
from ridings.models import Riding, Poll
from ballots.models import Ballot

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
