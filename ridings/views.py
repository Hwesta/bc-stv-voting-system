from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ridings.models import Riding, Poll, RidingForm, PollForm

# TODO Add decorators limiting access

# Riding Information

def view_all_ridings(request):
    #""" View summary information about all the ridings. """
    r = Riding.objects.all()
    return render_to_response('ridings/ridings.html',{'ridings': r, 'type': str('ridings')})

def view_riding(request, _id):
    #""" View all the details about a riding on one page. """
    r = Riding.objects.get(id=_id)
    return render_to_response('ridings/riding.html', {'riding': r})

def modify_riding(request, _id):
    riding = Riding.objects.get(id=_id)
    if request.method == 'POST':
	form = RidingForm(request.POST, instance=riding)
	if form.is_valid():
	    form.save()
	    return HttpResponseRedirect(reverse(view_all_ridings))
    else:
	form = RidingForm(instance=riding)
    return render(request, 'ridings/modify_riding.html', {'form': form, 'riding': riding, })

def delete_riding():
    """ Delete a riding. """
    pass


def add_riding(request):
    if request.method == 'POST':
	form = RidingForm(request.POST)
	if form.is_valid():
	    form.save()
	    return HttpResponseRedirect(reverse(view_all_ridings))
    else:
	form = RidingForm()
    return render(request, 'ridings/add_riding.html', {'form': form, })


# Poll Management

def view_polls(request):
    p = Poll.objects.all()
    return render_to_response('ridings/polls.html', {'polls': p, 'type':str('polls'), })

def add_poll(request):
    if request.method == 'POST':
	form = PollForm(request.POST)
	if form.is_valid():
	    form.save()
	    return HttpResponseRedirect(reverse(view_polls))
    else:
	form = PollForm()
    return render(request, 'ridings/add_poll.html', {'form': form, })

def modify_poll(request, _id):
    poll = Poll.objects.get(id=_id)
    if request.method == 'POST':
	form = PollForm(request.POST, instance=poll)
	if form.is_valid():
	    form.save()
	    return HttpResponseRedirect(reverse(view_polls))
    else:
	form = PollForm(instance=poll)
    return render(request, 'ridings/modify_poll.html', {'form': form, 'poll': poll, })



# Searching and Reports


