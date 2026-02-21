import os
from flask import Blueprint, render_template, g
from routes.utils import admin_required

bp = Blueprint("admin", __name__)

@bp.get("/admin")
@admin_required
def admin_home():
    admin_hint = os.getenv("ADMIN_HINT", "hint: set ADMIN_HINT in .env")
    return render_template("admin.html", user=g.user, admin_hint=admin_hint)

@bp.get("/admin/secret")
@admin_required
def admin_secret():
    final_flag = os.getenv("FINAL_FLAG", "flag{set_FINAL_FLAG_in_env}")
    return render_template("admin_secret.html", user=g.user, final_flag=final_flag)