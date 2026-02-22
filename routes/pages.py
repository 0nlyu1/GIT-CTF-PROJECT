from flask import Blueprint, render_template, g, request, redirect, url_for, flash, current_app
from routes.utils import login_required
from models import Submission, Challenge, User
from extensions import db
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

    # 기본 권한: 본인 제출만 열람 가능(CTF_MODE=0일 때만 강제)
    ctf_mode = bool(current_app.config.get("CTF_MODE", False))

    if (not ctf_mode) and (sub.user_id != g.user.id and g.user.role != "admin"):
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
    q = request.args.get("q")
    sort = request.args.get("sort", "score")

    rows = get_ranking(limit=100, q=q, sort=sort)

    # ---- Stage3: intended "query weakness" (CTF-safe) ----
    # 취지: 정렬 파라미터를 개발자가 "편의 기능"으로 파싱하다가 숨은 지시어가 먹히는 설계 실수
    ctf_mode = bool(current_app.config.get("CTF_MODE", False))
    stage3_token = str(current_app.config.get("STAGE3_TOKEN", "stage3-token-change-me"))
    stage3_hint = str(current_app.config.get("STAGE3_HINT", "hint: set STAGE3_HINT in .env"))

    stage3_unlocked = False
    if ctf_mode:
        # 예: sort=score|reveal:<token>
        raw = (sort or "")
        if "|reveal:" in raw:
            provided = raw.split("|reveal:", 1)[1].strip()
            stage3_unlocked = (provided != "" and provided == stage3_token)

    return render_template(
        "ranking.html",
        rows=rows,
        user=g.user,
        q=q,
        sort=sort,
        stage3_unlocked=stage3_unlocked,
        stage3_hint=stage3_hint if stage3_unlocked else None,
    )

@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        nickname = (request.form.get("nickname") or "").strip()

        # (선택) 너무 긴 값 방지: DB 컬럼이 String(80)
        if len(nickname) > 80:
            flash("닉네임은 80자 이내로 해줘.")
            return redirect(url_for("pages.profile"))

        g.user.nickname = nickname if nickname != "" else None
        db.session.commit()
        flash("저장됐어.")
        return redirect(url_for("pages.profile"))

    return render_template("profile.html", user=g.user)