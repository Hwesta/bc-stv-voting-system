# Django
from django import forms
from django.db import models
from django.forms import ModelForm
from django.core.validators import MinValueValidator, MaxValueValidator
# Election
from ridings.models import Riding, Poll
from ballots.models import Ballot

STATUS_CHOICES = (
    ('BEF', 'before'),
    ('DUR', 'during '),
    ('AFT', 'after '),
    ('ARC', 'archived'),
)
# State machine:
# BEF -> DUR -> AFT -> ARC
class Election(models.Model):
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='BEF')
    description = models.CharField(max_length=128, verbose_name="Name", help_text="For later identification")
    start = models.DateField(verbose_name="Date", help_text="Start date of the election.  Format: YYYY-MM-DD")
    # recount_threshold = models.DecimalField(max_digits=4, decimal_places=2,
        # verbose_name="Recount Threshold",
        # help_text="Percentage (0.00% to 99.99%) of difference to initiate a recount atuomatically.",
        # validators=[MinValueValidator(0.00),MaxValueValidator(99.99)],
        # default=0.01)
        
    recount_threshold = models.FloatField(verbose_name="Recount Threshold",
        help_text="Percentage (0.00% to 99.99%) of difference to initiate a recount atuomatically.",
        validators=[MinValueValidator(0.00),MaxValueValidator(99.99)],
        default=0.01)
        
    
    def __unicode__(self):
        return "Election "+self.status
    
    def change_status(self):
        """ Move the election to the next status. """
        
        #Check some preconditions for starting an election.
        bad_ridings={}
        other_errors=[]
        no_candidates = False
        too_few_candidates = False
        no_polls = False
        no_ridings = False
        
        if Riding.objects.filter(delete=False).count()==0:
            no_ridings = True
            other_errors.append('Can not start an election with no ridings.')
        
        for a_riding in Riding.objects.filter(delete=False):   
            if a_riding.num_candidates()==0:
                no_candidates = True
                if not a_riding in bad_ridings:
                    bad_ridings[a_riding]=[]
                bad_ridings[a_riding].append(' has no candidates.')
            elif a_riding.num_seats>a_riding.num_candidates():
                too_few_candidates = True
                if not a_riding in bad_ridings:
                    bad_ridings[a_riding]=[]
                bad_ridings[a_riding].append(' has too few candidates.')
            if a_riding.num_polls()==0:
                no_polls = True
                if not a_riding in bad_ridings:
                    bad_ridings[a_riding]=[]
                bad_ridings[a_riding].append(' has no polls.')        

        if self.status == 'BEF' and not no_candidates and not too_few_candidates and not no_polls and not no_ridings:
            # activate all not-deleted ridings
            ridings = Riding.objects.filter(delete=False)            
            # activate all not-deleted polls, that belong to a not-deleted riding
            polls = Poll.objects.filter(delete=False,riding__delete=False)
            for riding in ridings:
                riding.active = True
                riding.save()
            for poll in polls:
                poll.active = True
                poll.save()
            self.status = 'DUR'
        elif self.status == 'DUR':
            all_closed = True
            no_recounts = True
            for a_riding in Riding.objects.filter(delete=False, active=True):
                all_closed = False
                if not a_riding in bad_ridings:
                    bad_ridings[a_riding]=[]
                bad_ridings[a_riding].append(' is still active.')

            for a_riding in Riding.objects.filter(delete=False, recount_needed=True):
                no_recounts = False
                if not a_riding in bad_ridings:
                    bad_ridings[a_riding]=[]
                bad_ridings[a_riding].append(' has a recount pending.')
            
            if all_closed and no_recounts:
                self.status = 'AFT'
        elif self.status == 'AFT':
            self.status = 'ARC'
        elif self.status == 'ARC':
            pass
        else:
            self.status = 'BEF'
        
        return (bad_ridings, other_errors,)
   
    def archive(self):
        """ Archive an election """
        # TODO
        pass

    class meta:
        unique_together = (('status', 'description'))

class RecountForm(forms.Form):
    riding = forms.ModelChoiceField(queryset=Riding.objects.filter(active=False,delete=False))

class ElectionForm(ModelForm):
    class Meta:
        model = Election
        exclude = ('status', )



def define_view_permissions(allowed_groups, allowed_status):
    ''' Defines the permissions for a view.
    If either input is empty, it means ALL values are permitted for that field.

    allowed_groups is a set
    allowed_status is a STATUS_CHOICES'''
    allowed_groups = set(allowed_groups)
    allowed_status = set(allowed_status)
    # TODO: Change to intersection of wanted groups and have groups.
    def func(user):
        if user == None:
            return False
        if user.is_staff or user.is_superuser:
            return True
        election = Election.objects.all()
        election_status = str(election[0].status)
        user_groups = set([_.name for _ in user.groups.all()])
        allowed = True
        if len(allowed_groups) > 0 and user_groups.isdisjoint(allowed_groups):
            allowed = False
        if len(allowed_status) > 0 and election_status not in allowed_status:
            allowed = False
        return allowed
    return func

def permissions_and(perm1, perm2):
    def f(u):
        return perm1(u) and perm2(u)
    return f
def permissions_or(perm1, perm2):
    def f(u):
        return perm1(u) or perm2(u)
    return f

def permission_always(u):
    return True
