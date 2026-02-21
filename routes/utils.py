from functools import wraps
from flask import session, redirect, url_for, g
from models import User

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return User.query.get(uid)

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login_form"))
        g.user = user
        return view_func(*args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login_form"))
        if user.role != "admin":
            return redirect(url_for("challenges.list_challenges"))
        g.user = user
        return view_func(*args, **kwargs)
    return wrapper