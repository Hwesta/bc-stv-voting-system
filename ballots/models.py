from django.db import models
from django import forms
from ridings.models import Poll
from jsonfield import JSONField
from django.forms import ModelForm
from django.contrib.auth.models import User

class Ballot(models.Model):
    
    ballot_num = models.IntegerField()
    poll = models.ForeignKey(Poll)
    verified = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)
    # Vote will store a list of ranking: candidate pairs
    spoiled = models.BooleanField(default=False)
    # JSONField will not load back properly, and we are decoding the contents anyway
    vote = models.TextField()
    entered_by = models.ForeignKey(User, null=True, blank=True)
    ballot_hash = models.CharField(max_length=128, null=True, blank=True)
    

    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.verified)+", "+str(self.vote)

    def clean_vote(self):
        """
        Sum from 1..n->(n*(n+1))/2
        This means that if a ballot is valid, then the sum of the entries should equal that.
        """
        vote_data=self.cleaned_data['vote']
        print vote_data
        
        return vote_data

    def clean_entered_by(self):

        
        return self.clean_data['entered_by']
            

class BallotForm(ModelForm):
    class Meta:
        model = Ballot
        fields = ('poll', 'ballot_num', 'vote', 'spoiled')
        hidden = ('vote')

class ChoosePollForm(forms.Form):
    poll = forms.ModelChoiceField(Poll.objects.all())
