from __future__ import annotations

from datetime import datetime
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user", index=True)  # 'user' | 'admin'
    nickname = db.Column(db.String(80), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    submissions = db.relationship("Submission", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.username} role={self.role}>"


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=100, index=True)
    flag_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    submissions = db.relationship("Submission", back_populates="challenge", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Challenge {self.id} {self.title} ({self.points})>"


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True)

    submitted_answer = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("User", back_populates="submissions")
    challenge = db.relationship("Challenge", back_populates="submissions")

    __table_args__ = (
        db.Index("ix_submissions_user_challenge_correct", "user_id", "challenge_id", "is_correct"),
        db.Index("ix_submissions_user_created", "user_id", "created_at"),
        db.Index("ix_submissions_challenge_created", "challenge_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Submission {self.id} u={self.user_id} c={self.challenge_id} correct={self.is_correct}>"