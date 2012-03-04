from django.shortcuts import render_to_response  
from election.models import Riding, Person, Election, Poll, Ballot

def index(request):
    polls = Poll.objects.all()
    people = Person.objects.all()
    ballots = Ballot.objects.all()
    return render_to_response('index.html', 
        { 'polls' : polls,
          'people' : people,
          'ballots' : ballots, })
