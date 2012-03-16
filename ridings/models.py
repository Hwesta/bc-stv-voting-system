from django.db import models

class Riding(models.Model):
    name = models.CharField(max_length=128)
    #map = models.ImageField(upload_to="??")
    created = models.DateField()
    num_voters = models.IntegerField(help_text="Number of eligible voters.")
    num_seats = models.IntegerField(help_text="Number of seats available.")
    active = models.BooleanField(help_text="Whether an election is accepting ballots.")

    # These could be functions??
    num_ballots = models.IntegerField(help_text="Number of ballots cast.",
        default=0)
    num_ballots_spoiled = models.IntegerField(help_text="Number of ballots spoiled.",
        default=0)

    def __unicode__(self):
        return self.name

    def candidates(self):
        """ Return all the candidates in the riding. """
        return self.person_set.filter(is_candidate=True)
    def num_candidates(self):
        """ Return the number of candidates in the riding. """
        return self.person_set.filter(is_candidate=True).count()

    def incumbents(self):
        """ Return all the incumbents in the riding. """
        return self.person_set.filter(is_incumbent=True)
    def num_incumbents(self):
        """ Return the number of incumbents in the riding. """
        return self.person_set.filter(is_incumbent=True).count()

    def polls(self):
        """ Return all the polls in the riding. """
        return self.poll_set
    def num_polls(self):
        """ Return the number of polls in the riding. """
        return self.poll_set.count()

    def calculate_results(self):
        """ Determine who gets elected. """
        pass

class Poll(models.Model):
    riding = models.ForeignKey(Riding)
    active = models.BooleanField(help_text="Whether the poll is still accepting ballots.")
    polling_stn = models.CharField(max_length=128)
    
    def __unicode__(self):
        return str(self.riding)+", "+str(self.id)

