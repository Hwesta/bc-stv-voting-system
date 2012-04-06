from django.db import models
from django import forms
from ridings.models import Poll, Riding
from politicians.models import Politician
from jsonfield import JSONField
from django.forms import ModelForm
from django.contrib.auth.models import User
import json
from django.db import IntegrityError

BALLOT_STATE_CHOICES = (
    ('U', 'Unverified'),
    ('C', 'Correct'),
    ('I', 'Incorrect'),
    ('R', 'Recount'),
)
# State machine:
# U -> C
# U -> I
# (U,C,I) -> R

class Ballot(models.Model):
    
    ballot_num = models.IntegerField(db_index=True)
    poll = models.ForeignKey(Poll, db_index=True)
    # State of ballot for verification
    state = models.CharField(max_length=1, choices=BALLOT_STATE_CHOICES, default='U', null=False, db_index=True)
    # Was the ballot spoiled/rejected?
    spoiled = models.BooleanField(default=False, db_index=True)
    # Vote will store a list of ranking: candidate pairs
    # JSONField will not load back properly, and we are decoding the contents anyway
    vote = models.TextField(blank=True,help_text="Contents of ballot, JSON as a string")
    entered_by = models.ForeignKey(User, null=True, blank=True, db_index=True,help_text="Which RO entered the ballot")
    ballot_hash = models.CharField(max_length=128, null=True, blank=True)
    

    def __unicode__(self):
        return str(self.ballot_num)+", "+str(self.state)+", "+str(self.vote)

    def candidates_as_string(self):
        nice_string=[]
        candidates = Politician.objects.filter(candidate_riding=self.poll.riding)
        vote_json=json.loads(self.vote)
        for (k,v) in sorted(vote_json.iteritems(), key=lambda x:x[0]):
            if len(v)>0:
                candidate=candidates.get(id=int(v))
                nice_string.append("#"+str(k)+": "+candidate.name)
        return ", ".join(nice_string)

    def save(self, *args, **kwargs):
        me=self.entered_by
        conflicting_ballots=Ballot.objects.filter(ballot_num=self.ballot_num).filter(entered_by=me)
        if self.id is not None:
            conflicting_ballots=conflicting_ballots.exclude(id=self.id)        
        if len(conflicting_ballots)>0:
            raise IntegrityError('You have already entered this ballot.')
        super(Ballot, self).save(*args, **kwargs)
        

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
        return json.dumps(vote_data)


    def clean(self):
        cleaned_data = super(BallotForm, self).clean()
        got_vote = True
        # This is still messy
        if 'vote' not in cleaned_data:
            got_vote = False
            pass
        elif isinstance(cleaned_data['vote'], dict):
            vote_data = cleaned_data['vote']
        elif isinstance(cleaned_data['vote'], basestring):
            try:
                v = cleaned_data['vote']
                vote_data=json.loads(v)
            except forms.ValidationError as e:
                raise e
            except Exception as e:
                raise forms.ValidationError("(clean) Could not parse vote data: "+ str(e))
        if got_vote and (len(vote_data.keys()) == 0 and not cleaned_data['spoiled']):
            raise forms.ValidationError("Invalid ballot: Empty but not spoiled?")
        if cleaned_data['spoiled']:
            cleaned_data['vote'] = {}
        if 'vote' in cleaned_data and isinstance(cleaned_data['vote'], dict):
            cleaned_data['vote'] = json.dumps(cleaned_data['vote'])
        return cleaned_data
    
    class Meta:
        model = Ballot
        fields = ('poll', 'ballot_num', 'vote', 'spoiled')
        hidden = ('vote')

class ChoosePollForm(forms.Form):
    poll = forms.ModelChoiceField(Poll.objects.all())

class ChooseRidingToVerifyForm(forms.Form):
    riding = forms.ModelChoiceField(Riding.objects.all())

class AcceptBallotForm(forms.Form):
    ballot = forms.ModelChoiceField(Ballot.objects.all())

# Very similar to a BallotForm
# but ballot_num and poll are immutable!
class LockedBallotForm(BallotForm):
    def __init__(self,  *args, **kwargs):
        super(LockedBallotForm, self).__init__(*args, **kwargs)
        # Stop users from changing on form
        self.fields['ballot_num'].widget.attrs['readonly'] = True
        self.fields['poll'].widget.attrs['readonly'] = True

    # if they inject it, ignore anyway
    #def clean_poll(self):
    #    return self.instance.poll

    ## if they inject it, ignore anyway
    #def clean_ballot_num(self):
    #    return self.instance.ballot_num
