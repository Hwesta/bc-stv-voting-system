from django.db import models

ROLE_CHOICES = (
    ('AD', 'Administrator'),
    ('RE', 'Reporter'),
    ('EO', 'Electoral Officer'),
    ('RO', 'Returning Officer'),
)
class User(models.Model):
    name = models.CharField(max_length=128)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    #authentication = ???
    

class Riding(models.Model):
    name = models.CharField(max_length=128)
    #map = models.ImageField(upload_to="??")
    created = models.DateField()
    num_voters = models.IntegerField(help_text="Number of eligible voters.")
    num_seats = models.IntegerField(help_text="Number of seats available.")

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

   
class Person(models.Model):
    name = models.CharField(max_length=128)
    party = models.CharField(max_length=128)
    is_candidate = models.BooleanField()
    candidate_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="candidate_riding")
    is_incumbent = models.BooleanField()
    incumbent_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="incumbent_riding")

    def __unicode__(self):
        return self.name

       
STATUS_CHOICES = (
    ('BEF', 'before'),
    ('DUR', 'during '),
    ('AFT', 'after '),
)
class Election(models.Model):
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    #archive = 


class Poll(models.Model):
    riding = models.ForeignKey(Riding)
    closed = models.BooleanField()
    polling_stn = models.CharField(max_length=128)
    
    def __unicode__(self):
        return str(self.riding)+", "+str(self.id)

    
class Ballot(models.Model):
    ballot_num = models.IntegerField()
    candidate = models.ForeignKey(Person)
    rank = models.IntegerField()
    poll = models.ForeignKey(Poll)
    spoiled = models.BooleanField(default=False)
    
    def __unicode__(self):
        return str(self.candidate)+", "+str(self.rank)

    