from __future__ import annotations

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, url_for
from flask.cli import with_appcontext

from extensions import db, migrate
from ranking import get_ranking
from routes.utils import current_user

from seed import run_seed

from routes.auth import bp as auth_bp
from routes.challenges import bp as challenges_bp
from routes.pages import bp as pages_bp
from routes.admin import bp as admin_bp


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    # ---- Core config ----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ctf.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ---- CTF Mode ----
    app.config["CTF_MODE"] = os.getenv("CTF_MODE", "0").lower() in ("1", "true", "yes", "on")
    app.config["STAGE1_KEY"] = os.getenv("STAGE1_KEY", "stage1-change-me")
    app.config["STAGE3_TOKEN"] = os.getenv("STAGE3_TOKEN", "stage3-token-change-me")
    app.config["STAGE3_HINT"] = os.getenv("STAGE3_HINT", "hint: go /admin/secret")

    # ---- Extensions ----
    db.init_app(app)
    migrate.init_app(app, db)

    # ------------------------
    # Routes
    # ------------------------
    @app.get("/")
    def home():
        user = current_user()
        if user is None:
            return redirect(url_for("auth.login_form"))
        return redirect(url_for("challenges.list_challenges"))

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


# ========================
# CLI Commands (module-level)
# ========================

@app.cli.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    print("[db] create_all done")


@app.cli.command("seed")
@with_appcontext
def seed_command():
    run_seed()
    print("[seed] done")