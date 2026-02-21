from __future__ import annotations
from routes.auth import bp as auth_bp
from routes.challenges import bp as challenges_bp
from routes.pages import bp as pages_bp

import os
from flask import Flask, jsonify
from dotenv import load_dotenv

from extensions import db, migrate
from models import User, Challenge, Submission
from seed import run_seed
from ranking import get_ranking


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ctf.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # ---- CLI Commands ----
    @app.cli.command("seed")
    def seed_command():
        """DB에 초기 데이터(admin/user/challenges) 넣기"""
        with app.app_context():
            run_seed()

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/api/ranking")
    def ranking_endpoint():
        # 나중에 템플릿으로 바꾸면 됨. 지금은 JSON으로 확인만.
        rows = get_ranking(limit=100)
        return jsonify([row.__dict__ for row in rows])

    # ---- Register Blueprints ----
    app.register_blueprint(auth_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(pages_bp)
    return app

app = create_app()