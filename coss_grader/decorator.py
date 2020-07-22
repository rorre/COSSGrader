from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user


def authenticated_only():
    if not current_user.is_authenticated:
        return redirect(url_for("user.login"))


def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.is_admin):
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def authenticated_only_route(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        return func(*args, **kwargs)

    return wrapper
