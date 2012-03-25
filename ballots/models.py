from django.db import models
from django import forms
from ridings.models import Poll
from jsonfield import JSONField
from django.forms import ModelForm

class Ballot(models.Model):
    
    ballot_num = models.IntegerField()
    poll = models.ForeignKey(Poll)
    verified = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    # Vote will store a list of ranking: candidate pairs
    spoiled = models.BooleanField(default=False)
    # JSONField will not load back properly, and we are decoding the contents anyway
    vote = models.TextField()

    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.verified)+", "+str(self.vote)

class BallotForm(ModelForm):
    class Meta:
        model = Ballot
        fields = ('ballot_num', 'vote', 'spoiled')
        hidden = ('vote')

class ChoosePollForm(forms.Form):
    poll = forms.ModelChoiceField(Poll.objects.all())
