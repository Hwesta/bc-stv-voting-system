from django.db import models
from ridings.models import Riding
from django.forms import ModelForm 

class Politician(models.Model):
    name = models.CharField(max_length=128)
    party = models.CharField(max_length=128)
    # This should be NULL if the politician is not a candidate
    candidate_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="candidate_riding", db_index=True)
    # This should be NULL if the politician is not an incumbent
    incumbent_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="incumbent_riding", db_index=True)
    delete = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        return self.name+", "+self.party+" candidate in "+str(self.candidate_riding)+" incumbent in "+str(self.incumbent_riding)


class Politician_Add_Form(ModelForm):
    class Meta:
        model = Politician
        exclude = ('delete',)

class Politician_Modify_Form(ModelForm):
    class Meta:
        model = Politician

