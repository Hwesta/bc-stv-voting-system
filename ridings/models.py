from django.db import models
from django.forms import ModelForm

class Riding(models.Model):
    name = models.CharField(max_length=128)
    #map = models.ImageField(upload_to="??")
    created = models.DateField(help_text="YYYY-MM-DD")
    num_voters = models.IntegerField(help_text="Number of eligible voters.")
    num_seats = models.IntegerField(help_text="Number of seats available.")
    active = models.BooleanField(help_text="Whether an election is accepting ballots.")
    delete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def candidates(self):
        """ Return all the candidates in the riding. """
        return self.candidate_riding.filter(candidate_riding__isnull=False)
    def num_candidates(self):
        """ Return the number of candidates in the riding. """
        return self.candidates().count()

    def incumbents(self):
        """ Return all the incumbents in the riding. """
        return self.incumbent_riding.filter(incumbent_riding__isnull=False)
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
        return self.ballots().count()

    def num_spoiled_ballots(self):
        """ Number of spoiled ballots cast in all polls in the riding. """
        return self.ballots().filter(spoiled=True).count()

    def calculate_results(self):
        """ Determine who gets elected. """
        pass

class Poll(models.Model):
    riding = models.ForeignKey(Riding)
    active = models.BooleanField(help_text="Whether the poll is still accepting ballots.")
    polling_stn = models.CharField(max_length=128)

    def __unicode__(self):
        return str(self.riding)+", "+str(self.id)

class RidingForm(ModelForm):
    class Meta:
        model = Riding
        exclude = ('active','num_ballots','num_ballots_spoiled')

class PollForm(ModelForm):
    class Meta:
        model = Poll
        exclude = ('riding',)

