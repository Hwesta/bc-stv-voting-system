from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count
from ridings.models import Riding, Poll
from ballots.models import Ballot, BallotForm, ChoosePollForm
from politicians.models import Politician

# Entering Ballots
# TODO Add decorators limiting access
def choose_poll(request):
    """ Enter the poll number to enter ballots for."""
    if request.method == 'POST':
        form = ChoosePollForm(request.POST)
        if form.is_valid():
            poll = form.cleaned_data['poll']
            return HttpResponseRedirect(reverse(input_ballot, args=(poll.id,)))
    else:
        form = ChoosePollForm()

    return render(request, 'ballots/choose_poll.html',
        {'form': form,
        })
    
def compare_ballot(request, b_id):
    ballot = Ballot.objects.get(id=b_id)
    ballot_list = Ballot.objects.filter(ballot_num=ballot.ballot_num)
    return render(request, 'ballots/compare.html', {'ballots':ballot_list})

def close_poll():
    """ Close the poll and check all inputted ballots.

    Should be called once all ballots for a poll are entered.  Check if the
    ballots have been entered twice, and if so compare the results, generating
    a list of ballots that need ot be verified.
    """
    pass

def view_ballots(request):
    ballot_list = Ballot.objects.all()
    return render(request, 'ballots/view.html', {'ballots':ballot_list})

def view_ballot(request, b_id):
    ballot = Ballot.objects.get(id=b_id)
    return render(request, 'ballots/view_single.html', {'ballot':ballot, 'ballot_num':b_id})

def input_ballot(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    candidates = Politician.objects.filter(candidate_riding=poll.riding)
    if request.method == 'POST':
        form = BallotForm(request.POST)
        if form.is_valid():
            new_ballot = form.save()
            return HttpResponseRedirect(reverse(view_ballots))
    else:
        form = BallotForm(initial={'poll': poll_id, 'vote': 'invalid'})
    return render(request, 'ballots/add.html', {
                'form':form,
                'candidates':candidates,
            })

def view_conflict_list(request):
    # General notes:
    # IMPORTANT:
    # All ballot fetches MUST contain exactly one of the following
    # - exclude(state='R')
    # - filter(state='x') where x != R
    # Otherwise you will get old recount ballots as well!
    # It needs to be inside the Raw SQL as well for correct processing

    # Pass 1: All ballots with state NOT 'recount', that exist only once
    ballots_entered_only_once = Ballot.objects.raw(" \
        SELECT id FROM ballots_ballot \
        INNER JOIN ( \
            SELECT \
                ballot_num, \
                COUNT(ballot_num) AS cnt \
            FROM ballots_ballot \
            WHERE state != 'R' \
            GROUP BY ballot_num \
            HAVING COUNT(ballot_num) < 2 \
        ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
    ")
    ids = map(lambda b: b.id, ballots_entered_only_once)
    ballots_entered_only_once = Ballot.objects.exclude(state='R').filter(id__in=ids)

    # Pass 2: Exclude pass 1, No mix of unverified/correct, unverified/correct
    ballot_invalid_state_mix = Ballot.objects.raw(" \
        SELECT id FROM ballots_ballot \
        INNER JOIN ( \
            SELECT \
                ballot_num, \
                COUNT(ballot_num) AS cnt \
            FROM ballots_ballot \
            WHERE state != 'R' \
            GROUP BY ballot_num, state \
            HAVING COUNT(ballot_num)=1 AND state='U' \
        ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
    ")
    ids = map(lambda b: b.id,ballot_invalid_state_mix)
    ballot_invalid_state_mix = Ballot.objects.exclude(state='R').exclude(id__in=ballots_entered_only_once).filter(id__in=ids)

    # Pass 3: Completion check
    # If this AND the above lists are empty
    # We have completed all validation!
    # SELECT COUNT(*) AS cnt
    # FROM ballots_ballot
    # WHERE state = 'unverifed';
    unverified_count = Ballot.objects.filter(state='U').count()

    bad_ballots = list(ballots_entered_only_once) + list(ballot_invalid_state_mix)

    # Shortcut processing here
    if unverified_count == 0:
        return render(request, 'ballots/view_conflicts.html', {
            'bad': {
                'Single entry': ballots_entered_only_once,
                'Invalid state mix': ballot_invalid_state_mix,
            }
        })

    # Pass 4: Double-entry check
    # Each unverified ballot should exist twice by different RO
    # Yes, the docs say NOT to use string replacement,
    # But .raw params does not support lists!
    bad_ballot_nums = set(map(lambda b: b.ballot_num, bad_ballots))
    bad_ballot_nums_str_clause = ''
    if len(bad_ballots_nums) > 0:
        bad_ballot_nums_str = ','.join(map(str,bad_ballot_nums))
        bad_ballot_nums_str_clause = 'AND ballot_num NOT IN (%s)' %  (bad_ballot_nums_str ,))
    ballots_no_different_ro = Ballot.objects.raw(" \
        SELECT id FROM ballots_ballot \
        INNER JOIN ( \
            SELECT \
                ballot_num, \
                COUNT(DISTINCT entered_by_id) AS cnt \
            FROM ballots_ballot \
            WHERE state != 'R' %s \
            GROUP BY ballot_num \
            HAVING COUNT(DISTINCT entered_by_id) < 2 \
        ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
    " % (bad_ballot_nums_str_clause ,))
    ids = map(lambda b: b.id, ballots_no_different_ro)
    #ballots_no_different_ro_ballot_num = map(lambda b: b.ballot_num, ballots_no_different_ro)
    ballots_no_different_ro = Ballot.objects.exclude(state='R').filter(id__in=ids)

    bad_ballots = bad_ballots + list(ballots_no_different_ro)
   
    # Pass 5: Conflict resolution - Automatic 
    # If we grab unverified ballots not caught so far
    # And they have matching (ballot_num, spoiled) or (ballot_num, vote)
    # We can auto-verify them
    bad_ballot_nums = set(map(lambda b: b.ballot_num, bad_ballots))
    bad_ballot_nums_str_clause = ''
    if len(bad_ballots_nums) > 0:
        bad_ballot_nums_str = ','.join(map(str,bad_ballot_nums))
        bad_ballot_nums_str_clause = 'AND ballot_num NOT IN (%s)' %  (bad_ballot_nums_str ,))
    ballots_spoiled_auto_approve = Ballot.objects.raw(" \
        SELECT id FROM ballots_ballot \
        INNER JOIN ( \
            SELECT \
                ballot_num, \
                COUNT(spoiled) AS cnt, \
                COUNT(DISTINCT spoiled) AS cnt_d \
            FROM ballots_ballot \
            WHERE state='U' AND spoiled=1 %s \
            GROUP BY ballot_num, spoiled \
            HAVING COUNT(spoiled)=2 AND COUNT(DISTINCT spoiled)=1 \
        ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
    " % (bad_ballot_nums_str_clause ,))
    ballots_vote_auto_approve = Ballot.objects.raw(" \
        SELECT id FROM ballots_ballot \
        INNER JOIN ( \
            SELECT \
                ballot_num, \
                COUNT(vote) AS cnt, \
                COUNT(DISTINCT vote) AS cnt_d \
            FROM ballots_ballot \
            WHERE state='U' AND spoiled=0 %s \
            GROUP BY ballot_num, vote \
            HAVING COUNT(vote)=2 AND COUNT(DISTINCT vote)=1 \
        ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
    " % (bad_ballot_nums_str_clause ,))
    ids = map(lambda b: b.id, ballots_spoiled_auto_approve) + map(lambda b: b.id, ballots_vote_auto_approve)
    ballots_auto_approve = Ballot.objects.filter(state='U').filter(id__in=ids)

    # Pass 6: Conflict resolution - Manual
    # Remaining unverified items
    # - 2 unique ROs
    # - (2 unique votes) OR (2 uniques spoiled)
    # - Exclude ballots_auto_approve
    ballots_manual_approve = Ballot.objects.raw(" \
        SELECT id FROM ballots_ballot \
        INNER JOIN ( \
            SELECT \
                ballot_num, \
                COUNT(DISTINCT entered_by_id) AS cnt_ro, \
                COUNT(DISTINCT vote) as cnt_v, \
                COUNT(DISTINCT spoiled) as cnt_s \
            FROM ballots_ballot \
            WHERE state = 'U' \
            GROUP BY ballot_num \
            HAVING COUNT(DISTINCT entered_by_id)= 2 AND (COUNT(DISTINCT vote) = 2 OR COUNT(DISTINCT spoiled) = 2) \
        ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
    ")
    ids = map(lambda b: b.id, ballots_manual_approve)
    ballots_manual_approve = Ballot.objects.exclude(id__in=ballots_auto_approve).filter(state='U').filter(id__in=ids)

    return render(request, 'ballots/view_conflicts.html', {
        'bad': {
            'Single entry': ballots_entered_only_once,
            'Invalid state mix': ballot_invalid_state_mix,
            'Single RO only': ballots_no_different_ro,
        },
        'auto_ballots': ballots_auto_approve, 
        'manual_ballots': ballots_manual_approve
    })
