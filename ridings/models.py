from django import forms
from django.db import models
from django.forms import ModelForm
from django.db.models import Count, Max, Min
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


MAX_POLLS_PER_RIDING = 10000

class Riding(models.Model):
    name = models.CharField(max_length=128)
    #map = models.ImageField(upload_to="??")
    created = models.DateField(help_text="Date the riding was legislated into existance. Format: YYYY-MM-DD")
    num_voters = models.IntegerField(verbose_name="Voters", help_text="Number of eligible voters.")
    num_seats = models.IntegerField(verbose_name="Seats", help_text="Number of seats available.", validators=[MinValueValidator(1)])
    active = models.BooleanField(help_text="Whether a riding is accepting ballots.")
    delete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def candidates(self):
    #""" Return all the candidates in the riding. """
        return self.candidate_riding.filter(candidate_riding__isnull=False)

    def num_candidates(self):
        """ Return the number of candidates in the riding. """
        return self.candidates().filter(delete=False).count()

    def incumbents(self):
        """ Return all the incumbents in the riding. """
        return self.incumbent_riding.filter(incumbent_riding__isnull=False)

    def num_incumbents(self):
        """ Return the number of incumbents in the riding. """
        return self.incumbents().filter(delete=False).count()

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
        return "%s, #%d %s" % (str(self.riding), poll_num, self.polling_stn, )
        #return str(self.riding)+", "+str(self.polling_stn)+"

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
        exclude = ('active', 'delete',)

# Form for modifying a riding includeds delete flag
class Riding_Modify_Form(ModelForm):
    class Meta:
        model = Riding
        exclude = ('active',)

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
