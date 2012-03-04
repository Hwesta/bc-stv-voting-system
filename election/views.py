from django.shortcuts import render_to_response  
from election.models import Riding, Person, Election, Poll, Ballot

# TODO Add decorators limiting access

# General

def index(request):
    """ Display the index page. """
    polls = Poll.objects.all()
    people = Person.objects.all()
    ballots = Ballot.objects.all()
    return render_to_response('index.html', 
        { 'polls' : polls,
          'people' : people,
          'ballots' : ballots, })

# Entering Ballots

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


# Riding Information

def view_all_ridings():
    """ View summary information about all the ridings. """
    pass

def view_riding():
    """ View all the details about a riding on one page. """
    pass

def add_riding():
    """ Input information for a new riding. """
    pass

def modify_riding():
    """ Edit a riding's information. """
    pass

def delete_riding():
    """ Delete a riding. """
    pass


# Candidate/Incumbent Information
# NOTE Should we have one set of functions for incumbents and candidates,
# and just display different info based on a flag?


# Keyword Management



# Poll Management



# Searching and Reports



# Election Management



# User Management

def view_all_users():
    """ View summary information about all users. """
    pass

def add_user():
    """ Create a new user. """
    pass

def modify_user():
    """ Edit a user's information. """
    pass

def delete_user():
    """ Delete a user. """
    pass

def ban_user():
    """ Leave the user intact, but prevent them from logging in. """
    pass
