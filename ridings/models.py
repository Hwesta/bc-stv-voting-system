from django.db import models
from django.forms import ModelForm
from django.db.models import Count, Max, Min

MAX_POLLS_PER_RIDING = 10000

class Riding(models.Model):
    name = models.CharField(max_length=128)
    #map = models.ImageField(upload_to="??")
    created = models.DateField(help_text="Date the riding was legislated into existance. Format: YYYY-MM-DD")
    num_voters = models.IntegerField(verbose_name="Voters", help_text="Number of eligible voters.")
    num_seats = models.IntegerField(verbose_name="Seats", help_text="Number of seats available.")
    active = models.BooleanField(help_text="Whether a riding is accepting ballots.")
    delete = models.BooleanField(default=False)
    recount_needed = models.BooleanField(help_text="Is a recount required in this riding.")

    def __unicode__(self):
        return self.name

    def candidates(self):
        """ Return all the candidates in the riding. """
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

    def poll_range(self):
	polls = Poll.objects.filter(riding=self.name)
	num_polls = polls.count()
	return str(polls[0])+"-"+str(polls[num_polls - 1])

    def calculate_results(self):
        """ Determine who gets elected. """
        pass

class Poll(models.Model):
    riding = models.ForeignKey(Riding)
    active = models.BooleanField(help_text="Whether the poll is still accepting ballots.")
    poll_num = models.IntegerField(help_text="Number of polling station.", editable=False, null=True)
    polling_stn = models.CharField(max_length=128,help_text="Name of polling station.")

    def __unicode__(self):
        poll_num = int(-1 if self.poll_num is None else self.poll_num)
        return "%s, #%d %s" % (str(self.riding), poll_num, self.polling_stn, )
        #return str(self.riding)+", "+str(self.polling_stn)+"

    def save(self, *args, **kwargs):
        # Is this a create
        if self.poll_num is None:
            existing_max = Poll.objects.filter(riding=self.riding).annotate(max_poll_num=Max('poll_num')).values('max_poll_num').distinct()
            print existing_max
            if len(existing_max.all()) > 0:
                existing_max = existing_max[0]['max_poll_num']
            else:
                existing_max = None
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

# Form for adding/modifying a poll excludes choosing associated riding
class PollForm(ModelForm):
    class Meta:
        model = Poll
        exclude = ('riding',)

