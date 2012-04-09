from django.db import models
from ridings.models import Riding
from django.forms import ModelForm 

class Politician(models.Model):
    name = models.CharField(max_length=128)
    party = models.CharField(max_length=128)
    # This should be NULL if the politician is not a candidate
    candidate_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="candidate_riding", db_index=True,
        verbose_name="Candidate in riding",
        help_text="Leave blank if they are not a candidate.")
    # This should be NULL if the politician is not an incumbent
    incumbent_riding = models.ForeignKey(Riding, null=True, blank=True,
        related_name="incumbent_riding", db_index=True,
        verbose_name="Incumbent in riding",
        help_text="Leave blank if they are not an incumbent.")
    delete = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        display=self.name
        if self.candidate_riding != None:
            display+=", candidate in "+unicode(self.candidate_riding)
        if self.incumbent_riding != None:
            display+=", incumbent in "+unicode(self.incumbent_riding)
        return display


class Politician_Add_Form(ModelForm):
    class Meta:
        model = Politician
        exclude = ('delete',)
    def __init__(self, *args, **kwargs):
        super(Politician_Add_Form, self).__init__(*args, **kwargs)
        self.fields['candidate_riding'].queryset = Riding.objects.filter(delete=False)
        self.fields['incumbent_riding'].queryset = Riding.objects.filter(delete=False)

class Politician_Modify_Form(ModelForm):
    class Meta:
        model = Politician
    def __init__(self, *args, **kwargs):
        super(Politician_Modify_Form, self).__init__(*args, **kwargs)
        self.fields['candidate_riding'].queryset = Riding.objects.filter(delete=False)
        self.fields['incumbent_riding'].queryset = Riding.objects.filter(delete=False)
