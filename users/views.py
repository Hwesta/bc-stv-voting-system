from django.shortcuts import redirect, render
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test
from users.models import CreateUserForm, ModifyUserForm
from election.models import define_view_permissions, permission_always

# User Management
# TODO Add decorators limiting access

@user_passes_test(define_view_permissions(set(['ADMIN']),set(['BEF','DUR','AFT'])))
def index(request):
    """ View summary information about all users. """
    users = User.objects.filter(is_staff=False)
    return render(request, 'users/view_all_users.html',
        { 'users': users })

@user_passes_test(define_view_permissions(set(['ADMIN']),set(['BEF','DUR','AFT'])))
def view_user(request, user_id):
    """ View detailed information about one user. """
    return render(request, 'users/view_user.html',
        {  })

@user_passes_test(define_view_permissions(['ADMIN'],['BEF','DUR','AFT']))
def add_user(request):
    """ Create a new user. """
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(form.cleaned_data['username'], "user@invalid.com", form.cleaned_data['password1'])
            role = form.cleaned_data['role']
            group = Group.objects.get(name=role)
            new_user.groups.add(group)
            return redirect(index)
    else:
        form = CreateUserForm() 
    return render(request, 'users/add_user.html', {
        'form': form,
    })

@user_passes_test(define_view_permissions(set(['ADMIN']),set(['BEF','DUR','AFT'])))
def modify_user(request, user_id):
    """ Edit a user's information. """
    if request.method == 'POST':
        user = User.objects.get(id=user_id)
        form = ModifyUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(index)
    else:
        user = User.objects.get(id=user_id)
        form = ModifyUserForm(instance=user)

    return render(request, 'users/modify_user.html', {
        'form': form,
        'user_id': user_id,
    })

@user_passes_test(define_view_permissions(set(['ADMIN']),set(['BEF','DUR','AFT'])))
def delete_user(request, user_id):
    """ Delete a user. """
	# TODO: Missing
    return render(request, 'users/delete_user.html',
        {  })

@user_passes_test(define_view_permissions(set(['ADMIN']),set(['BEF','DUR','AFT'])))
def ban_user(request, user_id):
    """ Leave the user intact, but prevent them from logging in. """
	# TODO: Missing
    return render(request, 'users/ban_user.html',
        {  })

