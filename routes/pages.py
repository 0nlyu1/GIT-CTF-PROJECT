from flask import Blueprint, render_template, g
from routes.utils import login_required
from models import Submission, Challenge
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

@bp.get("/ranking")
@login_required
def ranking_page():
    rows = get_ranking(limit=100)
    return render_template("ranking.html", rows=rows, user=g.user)