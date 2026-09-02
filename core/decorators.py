from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='admin_login')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("You don't have access to this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def verifier_or_admin_required(view_func):
    @wraps(view_func)
    @login_required(login_url='verifier_login')
    def wrapper(request, *args, **kwargs):
        user = request.user
        is_verifier = hasattr(user, 'verifier_profile') and user.verifier_profile.is_active_verifier
        if not (user.is_superuser or is_verifier):
            return HttpResponseForbidden("You don't have access to this page.")
        return view_func(request, *args, **kwargs)
    return wrapper