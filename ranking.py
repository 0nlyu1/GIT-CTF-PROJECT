from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from sqlalchemy import func, and_
from extensions import db
from models import User, Challenge, Submission


@dataclass(frozen=True)
class RankingRow:
    user_id: int
    username: str
    nickname: str | None
    total_points: int
    # 타이브레이커: 마지막 정답 시간(더 빠른 사람이 우위) 같은 걸로 쓰고 싶으면 사용
    last_solve_at: Optional[str]


def get_ranking(limit: int = 100) -> List[RankingRow]:
    """
    규칙 R1:
      - (user_id, challenge_id)에서 '최초 정답 1건'만 점수 인정
      - total_points = 그 최초 정답들의 challenge.points 합
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

    # 2) 최초 정답 rows를 submissions + challenges에 조인해서 점수 합산
    #    또한 유저별 마지막 정답시간(max(first_correct_at))도 뽑아 타이브레이커로 쓸 수 있게.
    q = (
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
        .order_by(
            func.coalesce(func.sum(Challenge.points), 0).desc(),
            func.max(first_correct_subq.c.first_correct_at).asc(),  # 빨리 푼 사람이 위
            User.username.asc(),
        )
        .limit(limit)
    )

    rows = []
    for r in q.all():
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