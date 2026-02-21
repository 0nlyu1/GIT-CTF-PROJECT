from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import func, or_
from extensions import db
from models import User, Challenge, Submission


@dataclass(frozen=True)
class RankingRow:
    user_id: int
    username: str
    nickname: str | None
    total_points: int
    last_solve_at: Optional[str]


def get_ranking(
    limit: int = 100,
    q: str | None = None,
    sort: str = "score",
) -> List[RankingRow]:
    """
    규칙 R1:
      - (user_id, challenge_id)에서 '최초 정답 1건'만 점수 인정
      - total_points = 그 최초 정답들의 challenge.points 합

    ranking filters:
      - q: username/nickname 부분 검색
      - sort: 'score' | 'last' | 'user'
    """

    # 1) 유저-문제별 최초 정답 시간
    first_correct_subq = (
        db.session.query(
            Submission.user_id.label("user_id"),
            Submission.challenge_id.label("challenge_id"),
            func.min(Submission.created_at).label("first_correct_at"),
        )
        .filter(Submission.is_correct.is_(True))
        .group_by(Submission.user_id, Submission.challenge_id)
        .subquery()
    )

    # 2) 점수 합산 + last_solve_at
    q_base = (
        db.session.query(
            User.id.label("user_id"),
            User.username.label("username"),
            User.nickname.label("nickname"),
            func.coalesce(func.sum(Challenge.points), 0).label("total_points"),
            func.max(first_correct_subq.c.first_correct_at).label("last_solve_at"),
        )
        .outerjoin(first_correct_subq, first_correct_subq.c.user_id == User.id)
        .outerjoin(Challenge, Challenge.id == first_correct_subq.c.challenge_id)
        .group_by(User.id, User.username, User.nickname)
    )

    # 검색 필터(안전)
    if q:
        needle = f"%{q.strip()}%"
        q_base = q_base.filter(
            or_(
                User.username.ilike(needle),
                User.nickname.ilike(needle),
            )
        )

    # 정렬(allowlist)
    if sort == "last":
        q_base = q_base.order_by(
            func.coalesce(func.sum(Challenge.points), 0).desc(),
            func.max(first_correct_subq.c.first_correct_at).asc(),
            User.username.asc(),
        )
    elif sort == "user":
        q_base = q_base.order_by(
            User.username.asc(),
            func.coalesce(func.sum(Challenge.points), 0).desc(),
        )
    else:  # default: score
        q_base = q_base.order_by(
            func.coalesce(func.sum(Challenge.points), 0).desc(),
            func.max(first_correct_subq.c.first_correct_at).asc(),
            User.username.asc(),
        )

    q_base = q_base.limit(limit)

    rows: List[RankingRow] = []
    for r in q_base.all():
        rows.append(
            RankingRow(
                user_id=r.user_id,
                username=r.username,
                nickname=r.nickname,
                total_points=int(r.total_points or 0),
                last_solve_at=str(r.last_solve_at) if r.last_solve_at else None,
            )
        )
    return rows