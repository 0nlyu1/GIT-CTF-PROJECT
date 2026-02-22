import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from routes.utils import admin_required
from models import User
from extensions import db

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

@bp.get("/admin/review")
@admin_required
def admin_review():
    # Stage2는 CTF_MODE에서만 작동하게(안전장치)
    ctf_mode = os.getenv("CTF_MODE", "0").lower() in ("1", "true", "yes", "on")

    users = User.query.order_by(User.id.asc()).all()
    return render_template("admin_review.html", users=users, ctf_mode=ctf_mode)

@bp.post("/admin/review/<int:user_id>")
@admin_required
def admin_review_submit(user_id: int):
    ctf_mode = os.getenv("CTF_MODE", "0").lower() in ("1", "true", "yes", "on")
    if not ctf_mode:
        flash("CTF_MODE가 꺼져 있습니다.")
        return redirect(url_for("admin.admin_review"))

    u = User.query.get_or_404(user_id)

    stage2_token = os.getenv("STAGE2_TOKEN", "stage2-token-change-me")
    stage2_hint = os.getenv("STAGE2_HINT", "hint: set STAGE2_HINT in .env")

    nickname = (u.nickname or "")
    unlocked = (stage2_token in nickname)

    # 여기서는 취약 렌더/XSS가 아니라 "관리자 리뷰"라는 스토리로 다음 힌트를 연다.
    if unlocked:
        return render_template("admin_review_result.html", user=u, unlocked=True, stage2_hint=stage2_hint)

    return render_template("admin_review_result.html", user=u, unlocked=False, stage2_hint=None)