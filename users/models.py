from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AdminPasswordChangeForm
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm 

ROLE_CHOICES = (
    ('ADMIN', 'Administrator'),
    ('REP', 'Reporter'),
    ('EO', 'Electoral Officer'),
    ('RO', 'Returning Officer'),
)

class CreateUserForm(UserCreationForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES)

class ModifyUserForm(UserChangeForm):
    # Groups is present always
    #role = forms.ChoiceField(choices=ROLE_CHOICES)
    #groups = forms.ChoiceField(choices=ROLE_CHOICES)
    #groups = forms.ModelChoiceField(Group.objects.filter(name__in=[ _[0] for _ in ROLE_CHOICES]).all())
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput,
        help_text = "Enter the same password as above, for verification.", required=False)

    class Meta:
        model = User
        exclude = ('first_name', 'last_name', 'user_permissions', 'email', 'is_staff', 'is_active', 'is_superuser', 'password', 'last_login', 'date_joined')
    
    def __init__(self, *args, **kwargs):
        super(ModifyUserForm, self).__init__(*args, **kwargs)
        # Hide long message about permissions
        self.fields['groups'].help_text = "Select exactly one group"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def clean_groups(self):
        grp = self.cleaned_data["groups"]
        if isinstance(grp, basestring):
            grp = Group.objects.get(name=grp)
        if isinstance(grp, Group):
            grp = [grp]
        if len(grp) != 1:
            raise forms.ValidationError("Users must be in exactly one group.")
        return grp

    def save(self, commit=True):
        user = super(ModifyUserForm, self).save(commit=False)
        user.groups = self.cleaned_data["groups"]
        if len(self.cleaned_data["password1"]) > 0:
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
