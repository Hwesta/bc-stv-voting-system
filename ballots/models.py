from django.db import models
from django import forms
from ridings.models import Poll
from jsonfield import JSONField
from django.forms import ModelForm
from django.contrib.auth.models import User
import json

BALLOT_STATE_CHOICES = (
    ('U', 'Unverified'),
    ('C', 'Correct'),
    ('I', 'Incorrect'),
    ('R', 'Recount'),
)

class Ballot(models.Model):
    
    ballot_num = models.IntegerField(db_index=True)
    poll = models.ForeignKey(Poll)
    # State of ballot for verification
    state = models.CharField(max_length=1, choices=BALLOT_STATE_CHOICES, default='U', null=False, db_index=True)
    # Was the ballot spoiled/rejected?
    spoiled = models.BooleanField(default=False, db_index=True)
    # Vote will store a list of ranking: candidate pairs
    # JSONField will not load back properly, and we are decoding the contents anyway
    vote = models.TextField(blank=True)
    entered_by = models.ForeignKey(User, null=True, blank=True, db_index=True)
    ballot_hash = models.CharField(max_length=128, null=True, blank=True)
    

    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.state)+", "+str(self.vote)

def ids_sequential_and_start_at_1(lst):
    return set(lst) == set(range(1,len(lst)+1))
            

class BallotForm(ModelForm):

    def clean_vote(self):
        if 'vote' not in self.cleaned_data:
            raise forms.ValidationError("(clean_vote) vote missing from form input: ")
        try:
            if isinstance(self.cleaned_data['vote'], dict):
                vote_data = self.cleaned_data['vote']
            elif isinstance(self.cleaned_data['vote'], basestring):
                vote_data = json.loads(self.cleaned_data['vote'])
            vote = map(int, vote_data.keys())
            if len(vote) > 0 and not ids_sequential_and_start_at_1(vote):
                raise forms.ValidationError("Non-sequential vote entered.")
        except forms.ValidationError as e:
            raise e
        except Exception as e:
            raise forms.ValidationError("(clean_vote) Could not parse vote data: "+ str(e))
        return vote_data


    def clean(self):
        cleaned_data = super(BallotForm, self).clean()
        # This is still messy
        if 'vote' not in cleaned_data:
            raise forms.ValidationError("(clean) vote missing from form input: ")
        if isinstance(cleaned_data['vote'], dict):
            vote_data = cleaned_data['vote']
        elif isinstance(cleaned_data['vote'], basestring):
            try:
                v = cleaned_data['vote']
                vote_data=json.loads(v)
            except forms.ValidationError as e:
                raise e
            except Exception as e:
                raise forms.ValidationError("(clean) Could not parse vote data: "+ str(e))
        if len(vote_data.keys()) == 0 and not cleaned_data['spoiled']:
            raise forms.ValidationError("Invalid ballot: Empty but not spoiled?")
        if cleaned_data['spoiled']:
            cleaned_data['vote'] = {}
        """super(BallotForm, self).clean()
        print self._errors
        if self.cleaned_data.get('spoiled') and 'vote' in self._errors:
            del self._errors['vote']"""
        return self.cleaned_data

    """
    This function should ensure that a ballot can't be entered twice by the same RO.
    """
    '''def clean_entered_by(self):

        
        return self.clean_data['entered_by']'''
    
    class Meta:
        model = Ballot
        fields = ('poll', 'ballot_num', 'vote', 'spoiled')
        hidden = ('vote')

class ChoosePollForm(forms.Form):
    poll = forms.ModelChoiceField(Poll.objects.all())
