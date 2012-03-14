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
    #credentials = ???
    
    def __unicode__(self):
        return self.name+", "+self.role
    
    def __delete__(self):
        """ Delete this user. """
        pass
    
    def banUser(self):
        """ Leave the user account intact, but block them from logging in."""
        pass
    

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

   
class Politician(models.Model):
    name = models.CharField(max_length=128)
    party = models.CharField(max_length=128)
    # This should be null if the politician is not a candidate
    candidate_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="candidate_riding")
    # This should be null if the politician is not an incumbent
    incumbent_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="incumbent_riding")

    def __unicode__(self):
        return self.name

KEYWORD_TYPE = (
    ('RID', 'riding'),
    ('POL', 'politician'),
    )

class RidingKeywordList(models.Model):
    name = models.CharField(max_length=128)
    
    def __unicode__(self):
        return self.name

class RidingKeywordValue(models.Model):
   keyword = models.ForeignKey(RidingKeywordList)
   riding = models.ForeignKey(Riding)
   value = models.CharField(max_length=128)

   def __unicode__(self):
       return str(self.keyword)+" "+self.value
   class Meta:
        unique_together = (('riding','keyword'))

class PoliticianKeywordList(models.Model):
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class PoliticianKeywordValue(models.Model):
   keyword = models.ForeignKey(PoliticianKeywordList)
   politician = models.ForeignKey(Politician)
   value = models.CharField(max_length=128)

   def __unicode__(self):
       return str(self.keyword)+" "+self.value
   class Meta:
        unique_together = (('politician','keyword'))

    
STATUS_CHOICES = (
    ('BEF', 'before'),
    ('DUR', 'during '),
    ('AFT', 'after '),
)
class Election(models.Model):
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    description = models.CharField(max_length=128)
    start = models.DateField(help_text="Date the polls open")
    #archive = 
    
    def __unicode__(self):
        return "Election "+self.status
    
    def changeStatus(self):
        """ Move the election to the next status. """
        pass
    
    def archive(self):
        """ Archive an election """
        pass


class Poll(models.Model):
    riding = models.ForeignKey(Riding)
    active = models.BooleanField(help_text="Whether the poll is still accepting ballots.")
    polling_stn = models.CharField(max_length=128)
    
    def __unicode__(self):
        return str(self.riding)+", "+str(self.id)

    
class Ballot(models.Model):
    ballot_num = models.IntegerField()
    poll = models.ForeignKey(Poll)
    verified = models.BooleanField()
    # Vote will store a list of candidate : ranking pairs or a spoiled : true flag
    vote = models.TextField()
    
    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.verified)

    