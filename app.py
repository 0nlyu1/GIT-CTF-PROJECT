from __future__ import annotations

import os
from flask import Flask, jsonify, redirect, url_for
from dotenv import load_dotenv

from extensions import db, migrate
from models import User, Challenge, Submission
from seed import run_seed
from ranking import get_ranking
from routes.utils import current_user

from routes.auth import bp as auth_bp
from routes.challenges import bp as challenges_bp
from routes.pages import bp as pages_bp
from routes.admin import bp as admin_bp


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ctf.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


    # ---- CTF Mode ----
    app.config["CTF_MODE"] = os.getenv("CTF_MODE", "0").lower() in ("1", "true", "yes", "on")
    app.config["STAGE1_KEY"] = os.getenv("STAGE1_KEY", "stage1-change-me")
    app.config["STAGE3_TOKEN"] = os.getenv("STAGE3_TOKEN", "stage3-token-change-me")
    app.config["STAGE3_HINT"] = os.getenv("STAGE3_HINT", "hint: go /admin/secret")
    
    db.init_app(app)
    migrate.init_app(app, db)

    # ------------------------
    # 홈 라우트 (여기!)
    # ------------------------
    @app.get("/")
    def home():
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login_form"))
        return redirect(url_for("challenges.list_challenges"))

    # ---- CLI Commands ----
    @app.cli.command("seed")
    def seed_command():
        with app.app_context():
            run_seed()

    @app.get("/health")
    def health():
        return {"ok": True}

    @app.get("/api/ranking")
    def ranking_endpoint():
        rows = get_ranking(limit=100)
        return jsonify([row.__dict__ for row in rows])

    # ---- Register Blueprints ----
    app.register_blueprint(auth_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()