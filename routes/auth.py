from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User

bp = Blueprint("auth", __name__)

@bp.get("/login")
def login_form():
    return render_template("login.html")

@bp.post("/login")
def login_submit():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(username=username).one_or_none()
    if user is None or not user.check_password(password):
        flash("로그인 실패: 아이디/비밀번호 확인")
        return redirect(url_for("auth.login_form"))

    session["user_id"] = user.id
    return redirect(url_for("challenges.list_challenges"))

@bp.get("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth.login_form"))