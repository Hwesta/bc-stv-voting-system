from django.db import models
from ridings.models import Riding
from politicians.models import Politician
from django.forms import ModelForm
from django import forms

class RidingKeywordList(models.Model):
    """ The name of the keyword.

    For example, area, population,  This is the 'title on the column'."""
    name = models.CharField(max_length=128, db_index=True)
    delete = models.BooleanField()
    delete.default = False

    def __unicode__(self):
        return self.name

class RidingKeywordValue(models.Model):
    """ The value of a keyword for a particular riding. """
    keyword = models.ForeignKey(RidingKeywordList, db_index=True)
    riding = models.ForeignKey(Riding, db_index=True)
    value = models.CharField(max_length=128, db_index=True)

    def __unicode__(self):
        return str(self.keyword)+" "+str(self.riding)+" "+self.value
    class Meta:
        unique_together = (('riding','keyword'))

class PoliticianKeywordList(models.Model):
    """ The name of the keyword.

    For example, age, gender,  This is the 'title on the column'."""
    name = models.CharField(max_length=128, db_index=True)
    delete = models.BooleanField()
    delete.default = False

    def __unicode__(self):
        return self.name

class PoliticianKeywordValue(models.Model):
    """ The value of a keyword for a particular riding. """
    keyword = models.ForeignKey(PoliticianKeywordList, db_index=True)
    politician = models.ForeignKey(Politician, db_index=True)
    value = models.CharField(max_length=128, db_index=True)

    def __unicode__(self):
        return str(self.keyword)+" "+str(self.politician)+" "+self.value
    class Meta:
        unique_together = (('politician','keyword'))

class editRidingKeywordListForm(ModelForm):
    class Meta:
        model = RidingKeywordList


class addRidingKeywordListForm(ModelForm):
    class Meta:
        model = RidingKeywordList
        exclude = ('delete')

class editPoliticianKeywordListForm(ModelForm):
    class Meta:
        model = PoliticianKeywordList


class addPoliticianKeywordListForm(ModelForm):
    class Meta:
        model = PoliticianKeywordList
        exclude = ('delete')

class editRidingKeywordValueForm(ModelForm):
    class Meta:
        model = RidingKeywordValue
        exclude = ('keyword','riding')
        
class editPoliticianKeywordValueForm(ModelForm):
    class Meta:
        model = PoliticianKeywordValue
        exclude = ('keyword','politician')

class addRidingKeywordValueForm(ModelForm):
    class Meta:
        model = RidingKeywordValue
        widgets = {'riding': forms.HiddenInput()}

class addPoliticianKeywordValueForm(ModelForm):
    class Meta:
        model = PoliticianKeywordValue
        widgets = {'politician': forms.HiddenInput()}

class addhRidingKeywordValueForm(ModelForm):
    class Meta:
        model = RidingKeywordValue
        widgets = {'keyword': forms.HiddenInput()}

class addhPoliticianKeywordValueForm(ModelForm):
    class Meta:
        model = PoliticianKeywordValue
        widgets = {'keyword': forms.HiddenInput()}
        
class addaRidingKeywordValueForm(ModelForm):
    class Meta:
        model = RidingKeywordValue

class addaPoliticianKeywordValueForm(ModelForm):
    class Meta:
        model = PoliticianKeywordValue
