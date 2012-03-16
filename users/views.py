from django.shortcuts import render_to_response
from ridings.models import User

# User Management
# TODO Add decorators limiting access

def view_all_users():
    """ View summary information about all users. """
    pass

def add_user():
    """ Create a new user. """
    pass

def modify_user():
    """ Edit a user's information. """
    pass

def delete_user():
    """ Delete a user. """
    pass

def ban_user():
    """ Leave the user intact, but prevent them from logging in. """
    pass
