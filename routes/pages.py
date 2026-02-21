from flask import Blueprint, render_template, g, request, redirect, url_for, flash, current_app
from routes.utils import login_required
from models import Submission, Challenge, User

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
    안전한 설계(기본):
      - 본인 제출만 조회 가능
      - (퍼즐) CTF_MODE에서만 STAGE1_KEY를 맞추면 'Stage1 Leak' 섹션이 추가로 열림
    """
    sub = Submission.query.get_or_404(submission_id)

    # 기본 권한: 본인 제출만 열람 가능
    if sub.user_id != g.user.id and g.user.role != "admin":
        flash("권한이 없습니다.")
        return redirect(url_for("pages.my_submissions"))

    # -------- Stage1 Unlock (퍼즐) --------
    ctf_mode = bool(current_app.config.get("CTF_MODE", False))
    stage1_key = str(current_app.config.get("STAGE1_KEY", "stage1-change-me"))

    provided = (request.args.get("key") or "").strip()
    stage1_unlocked = (ctf_mode and provided != "" and provided == stage1_key)

    leaked = None
    if stage1_unlocked:
        # "다른 유저의 제출"을 실제로 뚫는 게 아니라,
        # 제작자가 의도한 1개 샘플만 보여주는 퍼즐 형태.
        # (seed에서 user2의 Warm-up 정답 제출이 존재한다는 전제)
        user2 = User.query.filter_by(username="user2").first()
        warmup = Challenge.query.filter_by(title="Warm-up").first()

        if user2 and warmup:
            leaked = (
                Submission.query
                .filter_by(user_id=user2.id, challenge_id=warmup.id, is_correct=True)
                .order_by(Submission.created_at.asc())
                .first()
            )

    return render_template(
        "submission_detail.html",
        sub=sub,
        user=g.user,
        ctf_mode=ctf_mode,
        stage1_unlocked=stage1_unlocked,
        leaked=leaked,
    )


@bp.get("/ranking")
@login_required
def ranking_page():
    rows = get_ranking(limit=100)
    return render_template("ranking.html", rows=rows, user=g.user)