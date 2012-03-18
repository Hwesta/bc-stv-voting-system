from django.db import models
from ridings.models import Poll
from jsonfield import JSONField
from django.forms import ModelForm

class Ballot(models.Model):
    
    ballot_num = models.IntegerField()
    poll = models.ForeignKey(Poll)
    verified = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    # Vote will store a list of candidate : ranking pairs or a spoiled : true flag
    vote = models.CharField(max_length=128)
    # vote = JSONField()

    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.verified)

class BallotForm(ModelForm):
    class Meta:
        model = Ballot
