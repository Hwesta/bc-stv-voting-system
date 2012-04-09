# Json
import json
# Django
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, Max, Min
from django.forms import ModelForm
# Droop
from droop.election import Election as DroopElection
from droop.profile import ElectionProfile as DroopElectionProfile
from droop.profile import ElectionProfileError as DroopElectionProfileError
# This is our BCSTV rules for Droop
from election.rules import BCSTVRule
# Election


MAX_POLLS_PER_RIDING = 10000

class Riding(models.Model):
    name = models.CharField(max_length=128)
    #map = models.ImageField(upload_to="??")
    created = models.DateField(help_text="Date the riding was legislated into existance. Format: YYYY-MM-DD")
    num_voters = models.IntegerField(verbose_name="Voters", help_text="Number of eligible voters.")
    num_seats = models.IntegerField(verbose_name="Seats", help_text="Number of seats available.", validators=[MinValueValidator(1)])
    active = models.BooleanField(help_text="Whether a riding is accepting ballots.")
    delete = models.BooleanField(default=False)
    recount_needed = models.BooleanField(help_text="Is a recount required in this riding.")


    def __unicode__(self):
        return self.name

    def candidates(self):
    #""" Return all the candidates in the riding. """
        return self.candidate_riding.filter(candidate_riding__isnull=False,delete=False)

    def num_candidates(self):
        """ Return the number of candidates in the riding. """
        return self.candidates().count()

    def incumbents(self):
        """ Return all the incumbents in the riding. """
        return self.incumbent_riding.filter(incumbent_riding__isnull=False,delete=False)

    def num_incumbents(self):
        """ Return the number of incumbents in the riding. """
        return self.incumbents().count()

    def polls(self):
        """ Return all the polls in the riding. """
        return self.poll_set.all()

    def num_polls(self):
        """ Return the number of polls in the riding. """
        return self.poll_set.count()

    def ballots(self):
        """ Return all of the ballots in all polls in the riding. """
        # Do not put this import at the toplevel!
        # It will break because ballots/models.py imports this file!
        from ballots.models import Ballot
        return Ballot.objects.filter(poll__in=self.polls())

    def num_ballots(self):
        """ Number of ballots cast in all polls in the riding. """
        # Be careful to distinguish it from rows
        return self.ballots().filter(state='C').values('ballot_num').distinct().count()

    def num_spoiled_ballots(self):
        """ Number of verified correct spoiled ballots cast in all polls in the riding. """
        return self.ballots().filter(spoiled=True,state='C').values('ballot_num').distinct().count()

    def poll_min(self):
        return (self._poll_minmaxcount())['minpoll']

    def poll_max(self):
        return (self._poll_minmaxcount())['maxpoll']

    def poll_range(self):
        polls = self.polls()
        minmax = self._poll_minmaxcount()
        minpoll = minmax['minpoll']
        maxpoll = minmax['maxpoll']
        num_polls = minmax['count']
        num_polls_closed = polls.filter(active=False,delete=False).count()
        if num_polls == 0:
            return "no polls"
        deleted_polls = polls.filter(delete=True)
        deleted_poll_list = ", ".join([ str(p) for p in [ p.poll_num or -1 for p in deleted_polls ]])
        s = "%d-%d" % (minpoll, maxpoll, )
        if deleted_poll_list != "":
            s += ", excluding %s due to deletion" % (deleted_poll_list, )
        if num_polls_closed > 0:
            s += " with %d poll%s closed." % (num_polls_closed, ("","s")[num_polls_closed>1], )
        return s
  
    def safe_to_close(self):
        verify_result = self.verify()
        unverified_ballots = [ballot for tmplist in verify_result.values() for ballot in tmplist]
        return len(unverified_ballots) == 0

    def verify(self):
        # Fix a Django MS-SQL bug first!
        # http://code.google.com/p/django-mssql/issues/detail?id=120
        from settings import DATABASES
        if DATABASES['default']['ENGINE'] == 'sqlserver_ado':
            from mssql_fix import fix_mssql_row_bug
            fix_mssql_row_bug()

        # Do not put this import at the toplevel!
        # It will break because ballots/models.py imports this file!
        from ballots.models import Ballot
        # General notes:
        # IMPORTANT:
        # All ballot fetches MUST contain exactly one of the following
        # - exclude(state='R')
        # - filter(state='x') where x != R
        # Otherwise you will get old recount ballots as well!
        # It needs to be inside the Raw SQL as well for correct processing
        poll_ids = self.poll_set.values('id').distinct()
        poll_ids_str = ",".join([str(x['id']) for x in poll_ids])

        # Pass 1: All ballots with state NOT 'recount', that exist only once
        ballots_entered_only_once = Ballot.objects.raw(" \
            SELECT id FROM ballots_ballot \
            INNER JOIN ( \
                SELECT \
                    ballot_num, \
                    COUNT(ballot_num) AS cnt \
                FROM ballots_ballot \
                WHERE state = 'U' AND poll_id IN (%s) \
                GROUP BY ballot_num \
                HAVING COUNT(ballot_num) < 2 \
            ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
        " % (poll_ids_str, ) )
        ids = map(lambda b: b.id, ballots_entered_only_once)
        ballots_entered_only_once = Ballot.objects.filter(state='U').filter(id__in=ids).filter(poll__in=poll_ids)

        # Pass 2: Exclude pass 1, No mix of unverified/correct, unverified/correct
        ballot_invalid_state_mix = Ballot.objects.raw(" \
            SELECT id FROM ballots_ballot \
            INNER JOIN ( \
                SELECT \
                    ballot_num, \
                    COUNT(ballot_num) AS cnt \
                FROM ballots_ballot \
                WHERE state != 'R' AND poll_id IN (%s) \
                GROUP BY ballot_num, state \
                HAVING COUNT(ballot_num)=1 AND state='U' \
            ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
        " % (poll_ids_str, ))
        ids = map(lambda b: b.id,ballot_invalid_state_mix)
        ballot_invalid_state_mix = Ballot.objects.exclude(state='R').exclude(id__in=ballots_entered_only_once).filter(id__in=ids).filter(poll__in=poll_ids)

        # Pass 3: Completion check
        # If this AND the above lists are empty
        # We have completed all validation!
        # SELECT COUNT(*) AS cnt
        # FROM ballots_ballot
        # WHERE state = 'unverifed';
        unverified_count = Ballot.objects.filter(state='U').filter(poll__in=poll_ids).count()

        bad_ballots = list(ballots_entered_only_once) + list(ballot_invalid_state_mix)

        if unverified_count == 0:
            return { 
                'single entry': ballots_entered_only_once,
                'invalid_state_mix': ballot_invalid_state_mix,
                'single_ro_only': [],
                'auto_ballots': [], 
                'manual_ballots': [],
                }

        # Pass 4: Double-entry check
        # Each unverified ballot should exist twice by different RO
        # Yes, the docs say NOT to use string replacement,
        # But .raw params does not support lists!
        bad_ballot_nums = set(map(lambda b: b.ballot_num, bad_ballots))
        bad_ballot_nums_str_clause = ''
        if len(bad_ballot_nums) > 0:
            bad_ballot_nums_str = ','.join(map(str,bad_ballot_nums))
            bad_ballot_nums_str_clause = 'AND ballot_num NOT IN (%s)' %  (bad_ballot_nums_str ,)
        ballots_no_different_ro = Ballot.objects.raw(" \
                SELECT id FROM ballots_ballot \
                INNER JOIN ( \
                SELECT \
                ballot_num, \
                COUNT(DISTINCT entered_by_id) AS cnt \
                FROM ballots_ballot \
                WHERE state = 'U' AND poll_id IN (%s) %s\
                GROUP BY ballot_num \
                HAVING COUNT(DISTINCT entered_by_id) < 2 \
                ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
                " % (poll_ids_str, bad_ballot_nums_str_clause ,))
        ids = map(lambda b: b.id, ballots_no_different_ro)
        #ballots_no_different_ro_ballot_num = map(lambda b: b.ballot_num, ballots_no_different_ro)
        ballots_no_different_ro = Ballot.objects.filter(state='U').filter(id__in=ids).filter(poll__in=poll_ids)

        bad_ballots = bad_ballots + list(ballots_no_different_ro)

        # Pass 5: Conflict resolution - Automatic 
        # If we grab unverified ballots not caught so far
        # And they have matching (ballot_num, spoiled) or (ballot_num, vote)
        # We can auto-verify them
        bad_ballot_nums = set(map(lambda b: b.ballot_num, bad_ballots))
        bad_ballot_nums_str_clause = ''
        if len(bad_ballot_nums) > 0:
            bad_ballot_nums_str = ','.join(map(str,bad_ballot_nums))
            bad_ballot_nums_str_clause = 'AND ballot_num NOT IN (%s)' %  (bad_ballot_nums_str ,)
        ballots_spoiled_auto_approve = Ballot.objects.raw(" \
                SELECT id FROM ballots_ballot \
                INNER JOIN ( \
                SELECT \
                ballot_num, \
                COUNT(spoiled) AS cnt, \
                COUNT(DISTINCT spoiled) AS cnt_d \
                FROM ballots_ballot \
                WHERE state='U' AND spoiled=1 AND poll_id IN (%s) %s \
                GROUP BY ballot_num, spoiled \
                HAVING COUNT(spoiled)=2 AND COUNT(DISTINCT spoiled)=1 \
                ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
        " % (poll_ids_str, bad_ballot_nums_str_clause ,))
        ballots_vote_auto_approve = Ballot.objects.raw(" \
            SELECT id FROM ballots_ballot \
            INNER JOIN ( \
                SELECT \
                    ballot_num, \
                    COUNT(vote) AS cnt, \
                    COUNT(DISTINCT vote) AS cnt_d \
                FROM ballots_ballot \
                WHERE state='U' AND spoiled=0 AND poll_id IN (%s) %s \
                GROUP BY ballot_num, vote \
                HAVING COUNT(vote)=2 AND COUNT(DISTINCT vote)=1 \
            ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
        " % (poll_ids_str, bad_ballot_nums_str_clause ,))
        ids = map(lambda b: b.id, ballots_spoiled_auto_approve) + map(lambda b: b.id, ballots_vote_auto_approve)
        ballots_auto_approve = Ballot.objects.filter(state='U').filter(id__in=ids).filter(poll__in=poll_ids)

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
                WHERE state = 'U' AND poll_id IN (%s) \
                GROUP BY ballot_num \
                HAVING COUNT(DISTINCT entered_by_id)= 2 AND (COUNT(DISTINCT vote) = 2 OR COUNT(DISTINCT spoiled) = 2) \
            ) q1 ON q1.ballot_num=ballots_ballot.ballot_num \
        " % (poll_ids_str, ))
        ids = map(lambda b: b.id, ballots_manual_approve)
        ballots_manual_approve = Ballot.objects.exclude(id__in=ballots_auto_approve).filter(state='U').filter(id__in=ids).filter(poll__in=poll_ids)

        return {
            'single_entry': ballots_entered_only_once,
            'invalid_state_mix': ballot_invalid_state_mix,
            'single_ro_only': ballots_no_different_ro,
            'auto_ballots': ballots_auto_approve, 
            'manual_ballots': ballots_manual_approve,
            }

    def calc_winners(self):
        # Import here to avoid loop in loading
        from politicians.models import Politician
        r = self
        # All ballots for a riding
        all_ballots = r.ballots()
        # All ballots for the calculation
        # TODO: Should this filtering move to the Riding class or Ballot class?
        calculation_ballots = all_ballots.filter(state='C').filter(spoiled=False)
        # All spoiled ballots
        # TODO: Should this filtering move to the Riding class or Ballot class?
        num_spoiled_ballots = r.num_spoiled_ballots()
        # All candidates for the riding
        c = self.candidates()
        # Get distinct ballot contents and how many times they occured
        b2 = calculation_ballots.values("vote").annotate(cnt=Count('vote'))
        # Dictionary of (key=droop candidate ID, value=politician.id)
        c2 = dict((i+1,v.id) for i, v in enumerate(list(c)))
        # Dictionary of (key=politician.id, value=droop candidate ID)
        c2b = dict((v,k) for k,v in c2.iteritems())
        fc_votes = {}
        for politician in c:
            fc_votes[politician.id] = 0

        # More sanity
        if r.num_seats < 1:
            raise DroopElectionProfileError("Too few Seats in " + r.name)
        if r.num_candidates() < r.num_seats:
            raise DroopElectionProfileError("Too few Candidates in " + r.name + ". " + str(r.num_seats) + " seats for " + str(r.num_candidates()) + " candidates.")
        #check if the number of ballots is enough for BCSTV
        if calculation_ballots.count() < (r.num_candidates() + 1):
            raise DroopElectionProfileError("Too few ballots to calculate BCSTV")

        # Start of BLT generation
        # Number of candidates, Number of seats
        data = str(c.count()) + " " + str(r.num_seats) + "\n"
        # For each distinct ballot content
        for ballot in b2:
            # Count of timesro_home.html
            data = data + str(ballot['cnt']) + " "
            # Content of ballot
            vote_line = json.loads(ballot['vote'])
            first = True
            for _i, _c in vote_line.iteritems():
                # Of the droop ID numbers for the candidate
                if _c == "":
                    # If empty, skip (empty line on ballot)
                    pass
                else:
                    data = data + str(c2b[int(_c)]) + " "
                    if first:
                        fc_votes[int(_c)] += ballot['cnt']
                        first = False

            # 0 to say no more candidates on ballot
            data = data + "0\n"
        # 0 to say no more ballots
        data = data + "0\n"

        # candidates in droop order
        for key, candidate in c2.iteritems():
            data = data + "\"" + unicode(candidate) + "\"\n"
        # Name of election
        data = data + "\"" + r.name + " Results\""
        # End of BLT generation
        try:
            E = DroopElection(DroopElectionProfile(data=data.encode('ascii', 'ignore')), dict(rule='bcstv'))
        except DroopElectionProfileError as e:
            raise e

        E.count()
        result = E.record()
        candidate_states = {}
        for i in range(len(result['actions'][-1]['cstate'])):
            temp = {}
            k = result['cdict'][i+1]['name']
            pol = Politician.objects.get(id = k)
            temp['droop_cstate'] = result['actions'][-1]['cstate'][i+1]
            temp['first_choice_votes'] = fc_votes[int(k)]
            temp['droop_id'] = i
            temp['cand_id'] = k
            candidate_states[pol] = temp

        return {
                'E': E, 
                'candidate_states': candidate_states, 
                'result': result, 
                'candidates': c,
                'num_spoiled_ballots': num_spoiled_ballots,
                'nballots': result['nballots'],
                'riding': self,
                }
    

    
    # Private
    def _poll_minmaxcount(self):
        return self.poll_set.aggregate(maxpoll=Max('poll_num'),minpoll=Min('poll_num'),count=Count('id'))

# no longer necessary
#    def calculate_results(self):
#        """ Determine who gets elected. """
#        pass

class Poll(models.Model):
    riding = models.ForeignKey(Riding)
    active = models.BooleanField(help_text="Whether the poll is still accepting ballots.")
    poll_num = models.IntegerField(help_text="Number of polling station.", editable=False, null=True)
    polling_stn = models.CharField(max_length=128,help_text="Name of polling station.")
    delete = models.BooleanField(default=False)

    def __unicode__(self):
        poll_num = int(-1 if self.poll_num is None else self.poll_num)
        return "%s, #%d" % (unicode(self.riding), poll_num)

    def close(self):
        # riding poll belongs to
        self.active = False
        self.save()
        # the # of polls belonging to the riding that are still active
        num_rem_polls = self.riding.poll_set.filter(active=True).exclude(delete=True).count()
        if num_rem_polls == 0:
            self.riding.active = False
            self.riding.save()

    def save(self, *args, **kwargs):
        # Is this a create
        if self.poll_num is None:
            existing_max = self.riding.poll_max()
            if existing_max is None:
                existing_max = self.riding.id * MAX_POLLS_PER_RIDING
            self.poll_num = existing_max+1
        super(Poll, self).save(*args, **kwargs)


# Form for adding a riding excludes delete flag (default = false)
class Riding_Add_Form(ModelForm):
    class Meta:
        model = Riding
        exclude = ('active', 'delete', 'recount_needed',)

# Form for modifying a riding includeds delete flag
class Riding_Modify_Form(ModelForm):
    class Meta:
        model = Riding
        exclude = ('active', 'recount_needed',)

# Form for adding a poll excludes choosing associated riding
class Poll_Add_Form(ModelForm):
    class Meta:
        model = Poll
        exclude = ('riding', 'active', 'delete',)

# Form for modifying a poll excludes choosing associated riding
class Poll_Modify_Form(ModelForm):
    class Meta:
        model = Poll
        exclude = ('riding', 'active',)

# Modified RecountForm
class ChooseRidingForm(forms.Form):
    riding = forms.ModelChoiceField(queryset=Riding.objects.filter(delete=False))
