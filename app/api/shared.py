import re

from flask import g, jsonify, request

from ..db import get_db

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,24}$")
TAG_PATTERN = re.compile(r"^[a-zа-яё0-9-]{2,24}$")


def error(message, status=400):
    return jsonify(error=message), status


def payload():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def current_user():
    if not g.user_id:
        return None
    return (
        get_db()
        .execute("SELECT id, username, email FROM users WHERE id = ?", (g.user_id,))
        .fetchone()
    )


def require_user():
    user = current_user()
    if user is None:
        return None, error("Войдите, чтобы продолжить", 401)
    return user, None


def parse_post(data):
    body = data.get("body", "")
    tags = data.get("tags", [])
    if not isinstance(body, str) or not 1 <= len(body.strip()) <= 1000:
        return None, None, "Текст должен содержать от 1 до 1000 символов"
    if not isinstance(tags, list) or len(tags) > 3:
        return None, None, "Можно указать не более трёх тегов"
    normalized = []
    for tag in tags:
        if not isinstance(tag, str) or not TAG_PATTERN.fullmatch(tag.strip().lower()):
            return (
                None,
                None,
                "Теги: 2–24 символа, латиница, кириллица, цифры или дефис",
            )
        name = tag.strip().lower()
        if name not in normalized:
            normalized.append(name)
    return body.strip(), normalized, None


def replace_tags(db, post_id, tags):
    db.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))
    for name in tags:
        db.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (name,))
        db.execute(
            "INSERT INTO post_tags(post_id, tag_id) SELECT ?, id FROM tags WHERE name = ?",
            (post_id, name),
        )


def post_record(row, db):
    result = dict(row)
    result["bookmarked"] = bool(result["bookmarked"])
    result["tags"] = [
        item["name"]
        for item in db.execute(
            "SELECT t.name FROM tags t JOIN post_tags pt ON pt.tag_id = t.id WHERE pt.post_id = ? ORDER BY t.name",
            (row["id"],),
        )
    ]
    return result


def get_post(db, post_id, viewer_id):
    row = db.execute(
        """
        SELECT p.id, p.author_id, p.body, p.created_at, p.updated_at, u.username,
               EXISTS(SELECT 1 FROM bookmarks b WHERE b.post_id = p.id AND b.user_id = ?) AS bookmarked
        FROM posts p JOIN users u ON u.id = p.author_id WHERE p.id = ?
        """,
        (viewer_id or 0, post_id),
    ).fetchone()
    return post_record(row, db) if row else None
