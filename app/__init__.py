import os
import secrets
from datetime import timedelta
from pathlib import Path

from flask import Flask, g, jsonify, request, session

from .db import close_db, init_db
from .db import init_app as init_db_app


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    default_database = (
        "/tmp/mayak.sqlite3"
        if os.environ.get("VERCEL")
        else str(Path(app.instance_path) / "microblog.sqlite3")
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get("DATABASE_PATH") or default_database,
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("APP_ENV") == "production",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    )
    if test_config:
        app.config.update(test_config)
    if (
        os.environ.get("APP_ENV") == "production"
        and not os.environ.get("SECRET_KEY")
        and not app.testing
    ):
        raise RuntimeError("SECRET_KEY must be set in production")
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    init_db_app(app)

    from .demo import seed_demo_command, seed_demo_data

    app.cli.add_command(seed_demo_command)

    from .api import api
    from .pages import pages

    app.register_blueprint(api)
    app.register_blueprint(pages)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
        if os.environ.get("AUTO_SEED_DEMO") == "1":
            seed_demo_data(os.environ.get("DEMO_PASSWORD", ""))

    @app.before_request
    def load_identity():
        g.user_id = session.get("user_id")
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        if (
            request.path.startswith("/api/")
            and request.method in {"POST", "PATCH", "PUT", "DELETE"}
            and not secrets.compare_digest(
                request.headers.get("X-CSRF-Token", ""), session["csrf_token"]
            )
        ):
            return jsonify(error="Неверный защитный токен. Обновите страницу."), 403

    @app.after_request
    def add_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        )
        return response

    @app.context_processor
    def inject_csrf():
        return {"csrf_token": session.get("csrf_token", "")}

    return app
