from django.db import models
from ridings.models import Riding
from politicians.models import Politician
from django.forms import ModelForm
from django import forms

class RidingKeywordList(models.Model):
    """ The name of the keyword.

    For example, area, population,  This is the 'title on the column'."""
    name = models.CharField(max_length=128, db_index=True)
    delete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class RidingKeywordValue(models.Model):
    """ The value of a keyword for a particular riding. """
    keyword = models.ForeignKey(RidingKeywordList, db_index=True)
    riding = models.ForeignKey(Riding, db_index=True)
    value = models.CharField(max_length=128, db_index=True)

    def __unicode__(self):
        return unicode(self.keyword)+" "+unicode(self.riding)+" "+self.value
    class Meta:
        unique_together = (('riding','keyword'))

class PoliticianKeywordList(models.Model):
    """ The name of the keyword.

    For example, age, gender,  This is the 'title on the column'."""
    name = models.CharField(max_length=128, db_index=True)
    delete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class PoliticianKeywordValue(models.Model):
    """ The value of a keyword for a particular riding. """
    keyword = models.ForeignKey(PoliticianKeywordList, db_index=True)
    politician = models.ForeignKey(Politician, db_index=True)
    value = models.CharField(max_length=128, db_index=True)

    def __unicode__(self):
        return unicode(self.keyword)+" "+unicode(self.politician)+" "+self.value
    class Meta:
        unique_together = (('politician','keyword'))

# RidingKeywordList
class editRidingKeywordListForm(ModelForm):
    class Meta:
        model = RidingKeywordList

class addRidingKeywordListForm(ModelForm):
    class Meta:
        model = RidingKeywordList
        exclude = ('delete')

# PoliticianKeywordList
class editPoliticianKeywordListForm(ModelForm):
    class Meta:
        model = PoliticianKeywordList


class addPoliticianKeywordListForm(ModelForm):
    class Meta:
        model = PoliticianKeywordList
        exclude = ('delete')

# RidingKeywordValue
# TODO find out what the differences between all these are and combine them
# so it's not so damn confusing
class editRidingKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(editRidingKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['riding'].queryset = Riding.objects.filter(delete=False)
        self.fields['keyword'].queryset = RidingKeywordList.objects.filter(delete=False)
        
    class Meta:
        model = RidingKeywordValue
        exclude = ('keyword','riding')
        
class addRidingKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(addRidingKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['riding'].queryset = Riding.objects.filter(delete=False)
        self.fields['keyword'].queryset = RidingKeywordList.objects.filter(delete=False)
        
    class Meta:
        model = RidingKeywordValue
        widgets = {'riding': forms.HiddenInput()}

class addhRidingKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(addhRidingKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['riding'].queryset = Riding.objects.filter(delete=False)
        self.fields['keyword'].queryset = RidingKeywordList.objects.filter(delete=False)

    class Meta:
        model = RidingKeywordValue
        widgets = {'keyword': forms.HiddenInput()}

class addaRidingKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(addaRidingKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['riding'].queryset = Riding.objects.filter(delete=False)
        self.fields['keyword'].queryset = RidingKeywordList.objects.filter(delete=False)
 
    class Meta:
        model = RidingKeywordValue

# PoliticianKeywordValue        
# TODO find out what the differences between all these are and combine them
# so it's not so damn confusing
class editPoliticianKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(editPoliticianKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['politician'].queryset = Politician.objects.filter(delete=False)
        self.fields['keyword'].queryset = PoliticianKeywordList.objects.filter(delete=False)
    class Meta:
        model = PoliticianKeywordValue
        exclude = ('keyword','politician')

class addPoliticianKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(addPoliticianKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['politician'].queryset = Politician.objects.filter(delete=False)
        self.fields['keyword'].queryset = PoliticianKeywordList.objects.filter(delete=False)
    class Meta:
        model = PoliticianKeywordValue
        widgets = {'politician': forms.HiddenInput()}

class addhPoliticianKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(addhPoliticianKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['politician'].queryset = Politician.objects.filter(delete=False)
        self.fields['keyword'].queryset = PoliticianKeywordList.objects.filter(delete=False)
    class Meta:
        model = PoliticianKeywordValue
        widgets = {'keyword': forms.HiddenInput()}
        
class addaPoliticianKeywordValueForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(addaPoliticianKeywordValueForm, self).__init__(*args, **kwargs)
        self.fields['politician'].queryset = Politician.objects.filter(delete=False)
        self.fields['keyword'].queryset = PoliticianKeywordList.objects.filter(delete=False)
    class Meta:
        model = PoliticianKeywordValue
