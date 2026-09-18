import re
import secrets
import sqlite3

from flask import jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from . import api
from .shared import USERNAME_PATTERN, current_user, error, payload


@api.get("/session")
def session_info():
    user = current_user()
    return jsonify(user=dict(user) if user else None, csrf_token=session["csrf_token"])


@api.post("/register")
def register():
    data = payload()
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    if not isinstance(username, str) or not USERNAME_PATTERN.fullmatch(username):
        return error("Имя: 3–24 символа, латиница, цифры или подчёркивание")
    if (
        not isinstance(email, str)
        or len(email) > 254
        or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)
    ):
        return error("Введите корректный адрес электронной почты")
    if not isinstance(password, str) or not 10 <= len(password) <= 128:
        return error("Пароль должен содержать от 10 до 128 символов")
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO users(username, email, password_hash) VALUES (?, ?, ?)",
            (username, email.lower(), generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.rollback()
        return error("Имя пользователя или почта уже заняты", 409)
    session.clear()
    session["user_id"] = cursor.lastrowid
    session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True
    return jsonify(
        user={"id": cursor.lastrowid, "username": username, "email": email.lower()}
    ), 201


@api.post("/login")
def login():
    data = payload()
    identity = data.get("identity", "")
    password = data.get("password", "")
    if not isinstance(identity, str) or not isinstance(password, str):
        return error("Введите имя или почту и пароль")
    user = (
        get_db()
        .execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ? OR email = ?",
            (identity.strip(), identity.strip()),
        )
        .fetchone()
    )
    if user is None or not check_password_hash(user["password_hash"], password):
        return error("Неверное имя пользователя или пароль", 401)
    session.clear()
    session["user_id"] = user["id"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    session.permanent = True
    return jsonify(
        user={"id": user["id"], "username": user["username"], "email": user["email"]}
    )


@api.post("/logout")
def logout():
    session.clear()
    return jsonify(ok=True)
