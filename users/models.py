from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

ROLE_CHOICES = (
    ('ADMIN', 'Administrator'),
    ('REP', 'Reporter'),
    ('EO', 'Electoral Officer'),
    ('RO', 'Returning Officer'),
)
class CreateUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES)
