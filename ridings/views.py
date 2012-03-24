from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from ridings.models import Riding, Poll, RidingForm, PollForm
from politicians.models import Politician
from keywords.models import RidingKeywordValue, PoliticianKeywordValue

# TODO Add decorators limiting access

# Riding Information

def view_all_ridings(request):
    #""" View list of all the ridings. """
    ridings = Riding.objects.filter(delete=False)
    return render_to_response('ridings/ridings.html',{'ridings': ridings, 'type': str('ridings')})

def view_deleted_ridings(request):
    #""" View list of deleted ridings. """
    ridings = Riding.objects.filter(delete=True)
    return render_to_response('ridings/deleted_ridings.html',{'ridings': ridings, 'type': str('ridings')})

def view_riding(request, r_id):
    #""" View all the details about a riding on one page. """
    riding = Riding.objects.get(id=r_id)
    polls = riding.polls()
    incumbents = riding.incumbents()
    candidates =riding.candidates()
    keywords = RidingKeywordValue.objects.filter(riding=riding)
    return render_to_response('ridings/riding.html',
        {'riding': riding,
         'polls': polls,
         'candidates': candidates,
         'incumbents': incumbents,
         'keywords': keywords,
        })

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

def view_polls(request, riding_id):
    riding = Riding.objects.get(id=riding_id)
    p = Poll.objects.filter(riding=riding)
    return render_to_response('ridings/polls.html',
        {'polls': p,
         'type': str('Polls'),
         'riding': riding,
        })

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
