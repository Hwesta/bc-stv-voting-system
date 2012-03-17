from django.db import models
from ridings.models import Poll
from jsonfield import JSONField

class Ballot(models.Model):
    ballot_num = models.IntegerField()
    poll = models.ForeignKey(Poll)
    verified = models.BooleanField()
    # Vote will store a list of candidate : ranking pairs or a spoiled : true flag
    vote = JSONField()

    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.verified)

    