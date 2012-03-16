from django.db import models

STATUS_CHOICES = (
    ('BEF', 'before'),
    ('DUR', 'during '),
    ('AFT', 'after '),
)
class Election(models.Model):
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    description = models.CharField(max_length=128)
    start = models.DateField(help_text="Date the polls open")
    #archive = 
    
    def __unicode__(self):
        return "Election "+self.status
    
    def changeStatus(self):
        """ Move the election to the next status. """
        pass
    
    def archive(self):
        """ Archive an election """
        pass


