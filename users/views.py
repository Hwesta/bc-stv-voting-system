from django.shortcuts import render_to_response, redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import CreateUserForm

# User Management
# TODO Add decorators limiting access

def index(request):
    """ View summary information about all users. """
    users = User.objects.filter(is_staff=False)
    return render(request, 'users/view_all_users.html',
        { 'users': users })

def view_user(request, user_id):
    """ View detailed information about one user. """
    return render_to_response('users/view_user.html',
        {  })

def add_user(request):
    """ Create a new user. """
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['password1'])
            return redirect(index)
    else:
        form = CreateUserForm() 
    return render(request, 'users/add_user.html', {
        'form': form,
    })


def modify_user(request, user_id):
    """ Edit a user's information. """
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            print "form clean", form.cleaned_data
            new_user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['password1'])
            print "new user", new_user
            return redirect(index)
    else:
        form = CreateUserForm(instance=request.user)

    return render(request, 'users/modify_user.html', {
        'form': form,
    })


def delete_user(request, user_id):
    """ Delete a user. """
    return render_to_response('users/delete_user.html',
        {  })


def ban_user(request, user_id):
    """ Leave the user intact, but prevent them from logging in. """
    return render_to_response('users/ban_user.html',
        {  })

