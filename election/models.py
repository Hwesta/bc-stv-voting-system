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



def define_view_permissions(groups, status):
    ''' Defines the permissions for a view.

    groups is a set
    status is a STATUS_CHOICES'''
    groups = set(groups)
    status = set(status)
    # TODO: Change to intersection of wanted groups and have groups.
    def func(user):
        if user == None:
            return False
        if user.is_staff or user.is_superuser:
            return True
        election = Election.objects.all()
        user_groups = user.groups.all()
        for i in range(0, (len(groups) - 1)):
            if (user_groups.count() > 0 and str(user_groups[i]) in groups) and (str(election[Election.objects.all().count() - 1].status) in status):
                return True
        return False
    return func


