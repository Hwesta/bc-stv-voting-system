from django.shortcuts import render_to_response
from users.models import User

# User Management
# TODO Add decorators limiting access

def index(request):
    """ View summary information about all users. """
    return render_to_response('users/view_all_users.html',
        {  })

def view_user(request, user_id):
    """ View detailed information about one user. """
    return render_to_response('users/view_user.html',
        {  })

def add_user(request):
    """ Create a new user. """
    return render_to_response('users/add_user.html',
        {  })

def modify_user(request, user_id):
    """ Edit a user's information. """
    return render_to_response('users/modify_user.html',
        {  })


def delete_user(request, user_id):
    """ Delete a user. """
    return render_to_response('users/delete_user.html',
        {  })


def ban_user(request, user_id):
    """ Leave the user intact, but prevent them from logging in. """
    return render_to_response('users/ban_user.html',
        {  })

