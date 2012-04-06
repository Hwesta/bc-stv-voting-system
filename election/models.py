from django.db import models
from django import forms
from ridings.models import Riding
from django.forms import ModelForm

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
    description = models.CharField(max_length=128)
    start = models.DateField(help_text="YYYY-MM-DD")
    #archive = 
    
    def __unicode__(self):
        return "Election "+self.status
    
    def changeStatus(self):
        """ Move the election to the next status. """
        if self.status == 'BEF':
            self.status = 'DUR'
        elif self.status == 'DUR':
            self.status = 'AFT'
        elif self.status == 'AFT':
            self.status = 'ARC'
        elif self.status == 'ARC':
            pass
        else:
            self.status = 'BEF'
    
    def archive(self):
        """ Archive an election """
        # TODO
        pass

    class meta:
        unique_together = (('status', 'description'))

class RecountForm(forms.Form):
    riding = forms.ModelChoiceField(queryset=Riding.objects.filter(active=False))

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
