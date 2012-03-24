from django.contrib.auth.backends import ModelBackend
from ipauth.backend import RangeBackend

class ElectionAuthBackend(object):
    """
    Authenticate against django.contrib.auth.backends.ModelBackend AND ipauth.backend.RangeBackend
    Users must pass both sets of authentication to use the system
    """
    supports_anonymous_user = False
    ipauth_backend = None
    model_backend = None

    def __init__(self):
        self.ipauth_backend = RangeBackend()
        self.model_backend = ModelBackend()
    
    def authenticate(self, username=None, password=None, ip=None):
        """
        Authenticate against multiple backends AND'd together
        TODO: Election admin
        """
        model_user = self.model_backend.authenticate(username=username, password=password)
        ip_user = self.ipauth_backend.authenticate(ip=ip)        
        if not model_user:
            return None
        if model_user.is_superuser: # TODO: Election admin
            return model_user
        if not ip_user:
            return None

    def get_group_permissions(self, user_obj):
        """
        Returns a set of permission strings that this user has through his/her
        groups.
        """
        return self.model_backend.get_group_permissions(user_obj)

    def get_all_permissions(self, user_obj):
        return self.model_backend.get_all_permissions(user_obj)

    def has_perm(self, user_obj, perm):
        return self.model_backend.has_perm(user_obj, perm)

    def has_module_perms(self, user_obj, app_label):
        return self.model_backend.has_module_perms(user_obj, app_label)

    def get_user(self, user_id):
        return self.model_backend.get_user(user_id)

# vim: ts=2 sts=2 sw=2 et:
