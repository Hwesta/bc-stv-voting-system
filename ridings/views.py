from django.shortcuts import render_to_response
from ridings.models import Riding, Poll, RidingForm

# TODO Add decorators limiting access

# Riding Information

def view_all_ridings(request):
    #""" View summary information about all the ridings. """
    r = Riding.objects.all()
    return render_to_response('ridings/ridings.html',{'ridings': r, 'type': str('Ridings')})

def view_riding(request, _id):
    #""" View all the details about a riding on one page. """
    r = Riding.objects.get(id=_id)
    return render_to_response('ridings/riding.html',{'riding': r})

def add_riding():
    """ Input information for a new riding. """
    pass

def modify_riding():
    """ Edit a riding's information. """
    pass

def delete_riding():
    """ Delete a riding. """
    pass


def add_riding(request):
    if request.method == 'POST':
	form = RidingForm(request.POST)
	if form.is_valid():
	    return HttpResponseRedirect('ridings/ridings.html')
    else:
	form = RidingForm()
    return render_to_response('ridings/add_riding.html', {'form': form, })

# Poll Management



# Searching and Reports


