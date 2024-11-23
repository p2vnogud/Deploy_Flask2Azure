# middlewares/middleware.py

from functools import wraps
from flask import session, redirect, url_for

def check_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('loggedin') == True:
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return wrapper
