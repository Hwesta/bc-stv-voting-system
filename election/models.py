from django.db import models
from django import forms
from ridings.models import Riding
from django.forms import ModelForm

STATUS_CHOICES = (
    ('BEF', 'before'),
    ('DUR', 'during '),
    ('AFT', 'after '),
)
class Election(models.Model):
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
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
        else:
            self.status = 'BEF'
    
    def archive(self):
        """ Archive an election """
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
    def func(user):
        election = Election.objects.all()
        if (user.groups.all()[0] in groups) and (election[0].status in status):
            return True
        else:
            return False
    return func


