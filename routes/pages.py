from flask import Blueprint, render_template, g, request, redirect, url_for, flash
from routes.utils import login_required
from extensions import db
from models import Submission, User
from ranking import get_ranking

bp = Blueprint("pages", __name__)


@bp.get("/my/submissions")
@login_required
def my_submissions():
    subs = (
        Submission.query
        .filter_by(user_id=g.user.id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    return render_template("my_submissions.html", subs=subs, user=g.user)


@bp.get("/submissions/<int:submission_id>")
@login_required
def submission_detail(submission_id: int):
    """
    정상 설계(보안): 본인 제출만 열람 가능.
    admin은 모두 열람 가능.
    """
    sub = Submission.query.get_or_404(submission_id)

    if g.user.role != "admin" and sub.user_id != g.user.id:
        flash("권한이 없습니다.")
        return redirect(url_for("pages.my_submissions"))

    return render_template("submission_detail.html", sub=sub, user=g.user)


@bp.get("/profile")
@login_required
def profile_page():
    return render_template("profile.html", user=g.user)


@bp.post("/profile")
@login_required
def profile_update():
    nickname = (request.form.get("nickname") or "").strip()

    if len(nickname) > 80:
        flash("닉네임은 80자 이하여야 합니다.")
        return redirect(url_for("pages.profile_page"))

    # 빈 문자열이면 NULL로 처리
    g.user.nickname = nickname if nickname else None
    db.session.commit()

    flash("닉네임이 저장되었습니다.")
    return redirect(url_for("pages.profile_page"))


@bp.get("/ranking")
@login_required
def ranking_page():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "score").strip()

    rows = get_ranking(limit=100, q=q if q else None, sort=sort)
    return render_template("ranking.html", rows=rows, user=g.user, q=q, sort=sort)