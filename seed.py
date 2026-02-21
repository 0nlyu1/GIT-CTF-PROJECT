from __future__ import annotations

import os
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, Challenge

# ⚠️ 레포 공개 시 실제 플래그를 그대로 올리기 싫으면:
# - 여기 값을 환경변수로 받아오게 하거나,
# - seed 실행 전에만 로컬에서 넣고 gitignore 처리.
DEFAULT_FLAGS = [
    "flag{mjsec_demo_1}",
    "flag{mjsec_demo_2}",
    "flag{mjsec_demo_3}",
]


def upsert_user(username: str, password: str, role: str = "user", nickname: str | None = None) -> User:
    user = User.query.filter_by(username=username).one_or_none()
    if user is None:
        user = User(username=username, role=role, nickname=nickname)
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
    else:
        # 필요 시 업데이트
        user.role = role
        if nickname is not None:
            user.nickname = nickname
    return user


def upsert_challenge(title: str, description: str, points: int, flag_plain: str, is_active: bool = True) -> Challenge:
    ch = Challenge.query.filter_by(title=title).one_or_none()
    if ch is None:
        ch = Challenge(
            title=title,
            description=description,
            points=points,
            flag_hash=generate_password_hash(flag_plain),  # flag 평문 대신 hash 저장
            is_active=is_active,
        )
        db.session.add(ch)
    else:
        ch.description = description
        ch.points = points
        ch.flag_hash = generate_password_hash(flag_plain)
        ch.is_active = is_active
    return ch


def run_seed() -> None:
    # 1) users
    upsert_user("admin", "admin1234", role="admin", nickname="Admin")
    upsert_user("user1", "user1234", role="user", nickname="alice")
    upsert_user("user2", "user1234", role="user", nickname="bob")

    # 2) challenges
    flags = [
        os.getenv("FLAG_1", DEFAULT_FLAGS[0]),
        os.getenv("FLAG_2", DEFAULT_FLAGS[1]),
        os.getenv("FLAG_3", DEFAULT_FLAGS[2]),
    ]

    upsert_challenge(
        title="Warm-up",
        description="첫 번째 문제. 간단한 기능/페이지에서 플래그를 찾으세요.",
        points=100,
        flag_plain=flags[0],
    )
    upsert_challenge(
        title="Ranking Twist",
        description="랭킹/점수 흐름을 관찰해보세요.",
        points=200,
        flag_plain=flags[1],
    )
    upsert_challenge(
        title="Admin Area",
        description="관리자 영역 어딘가에 답이 있습니다.",
        points=300,
        flag_plain=flags[2],
    )

    db.session.commit()
    print("[seed] done: users/admin + 3 challenges created/updated.")


if __name__ == "__main__":
    # 이 파일 단독 실행을 원하면 app context가 필요하므로 app.py 커맨드로 실행하는 걸 추천.
    print("Run via: flask seed")