from django.db import models

ROLE_CHOICES = (
    ('AD', 'Administrator'),
    ('RE', 'Reporter'),
    ('EO', 'Electoral Officer'),
    ('RO', 'Returning Officer'),
)
class User(models.Model):
    name = models.CharField(max_length=128)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    #credentials = ???

    def __unicode__(self):
        return self.name+", "+self.role

    def __delete__(self):
        """ Delete this user. """
        pass

    def banUser(self):
        """ Leave the user account intact, but block them from logging in."""
        pass
    