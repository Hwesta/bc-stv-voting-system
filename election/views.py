from django.shortcuts import render_to_response  
from election.models import Election

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


# Election Management



