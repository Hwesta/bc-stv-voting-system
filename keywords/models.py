from django.db import models
from ridings.models import Riding
from politicians.models import Politician
from django.forms import ModelForm

class RidingKeywordList(models.Model):
    """ The name of the keyword.

    For example, area, population,  This is the 'title on the column'."""
    name = models.CharField(max_length=128)
    delete = models.BooleanField()
    delete.default = False

    def __unicode__(self):
        return self.name

class RidingKeywordValue(models.Model):
    """ The value of a keyword for a particular riding. """
    keyword = models.ForeignKey(RidingKeywordList)
    riding = models.ForeignKey(Riding)
    value = models.CharField(max_length=128)

    def __unicode__(self):
        return str(self.keyword)+" "+str(self.riding)+" "+self.value
    class Meta:
        unique_together = (('riding','keyword'))

class PoliticianKeywordList(models.Model):
    """ The name of the keyword.

    For example, age, gender,  This is the 'title on the column'."""
    name = models.CharField(max_length=128)
    delete = models.BooleanField()
    delete.default = False
	
    def __unicode__(self):
        return self.name

class PoliticianKeywordValue(models.Model):
    """ The value of a keyword for a particular riding. """
    keyword = models.ForeignKey(PoliticianKeywordList)
    politician = models.ForeignKey(Politician)
    value = models.CharField(max_length=128)

    def __unicode__(self):
        return str(self.keyword)+" "+str(self.politician)+" "+self.value
    class Meta:
        unique_together = (('politician','keyword'))

class RidingKeywordListForm(ModelForm):
    class Meta:
        model = RidingKeywordList

class PoliticianKeywordListForm(ModelForm):
    class Meta:
        model = PoliticianKeywordList

class RidingKeywordValueForm(ModelForm):
    class Meta:
        model = RidingKeywordValue
        
class PoliticianKeywordValueForm(ModelForm):
    class Meta:
        model = PoliticianKeywordValue
