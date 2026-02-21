from flask import Blueprint, render_template, g
from routes.utils import admin_required

bp = Blueprint("admin", __name__)

@bp.get("/admin")
@admin_required
def admin_home():
    return render_template("admin.html", user=g.user)