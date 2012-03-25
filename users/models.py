from django import forms
from django.contrib.auth.forms import UserCreationForm

ROLE_CHOICES = (
    ('AD', 'Administrator'),
    ('RE', 'Reporter'),
    ('EO', 'Electoral Officer'),
    ('RO', 'Returning Officer'),
)
class CreateUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    #class Meta:
        #permissions = ROLE_CHOICES


    