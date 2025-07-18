from functools import wraps
from django.shortcuts import redirect

def login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if 'auth_key' in request.session or 'id_user' in request.session:
            return function(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrap
