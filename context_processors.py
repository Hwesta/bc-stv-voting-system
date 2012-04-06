from election.models import Election

def election_status(request):
    elec = Election.objects.all()
    return {'election': elec[0]}