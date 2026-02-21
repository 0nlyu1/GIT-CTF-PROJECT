from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from werkzeug.security import check_password_hash
from extensions import db
from models import Challenge, Submission
from routes.utils import login_required

bp = Blueprint("challenges", __name__)

@bp.get("/challenges")
@login_required
def list_challenges():
    challenges = Challenge.query.filter_by(is_active=True).order_by(Challenge.id.asc()).all()
    return render_template("challenges.html", challenges=challenges, user=g.user)

@bp.get("/challenges/<int:challenge_id>")
@login_required
def challenge_detail(challenge_id: int):
    ch = Challenge.query.get_or_404(challenge_id)
    return render_template("challenge_detail.html", ch=ch, user=g.user)

@bp.post("/challenges/<int:challenge_id>/submit")
@login_required
def submit_flag(challenge_id: int):
    ch = Challenge.query.get_or_404(challenge_id)
    answer = request.form.get("answer", "").strip()

    is_correct = check_password_hash(ch.flag_hash, answer)

    sub = Submission(
        user_id=g.user.id,
        challenge_id=ch.id,
        submitted_answer=answer,
        is_correct=is_correct,
    )
    db.session.add(sub)
    db.session.commit()

    flash("정답입니다!" if is_correct else "오답입니다.")
    return redirect(url_for("challenges.challenge_detail", challenge_id=ch.id))