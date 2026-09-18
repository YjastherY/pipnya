from flask import g, jsonify, request

from ..db import get_db
from . import api
from .shared import error, require_user


@api.get("/users/<username>")
def user_profile(username):
    db = get_db()
    user = db.execute(
        "SELECT id, username, created_at FROM users WHERE username = ?", (username,)
    ).fetchone()
    if user is None:
        return error("Пользователь не найден", 404)
    count_posts = db.execute(
        "SELECT COUNT(*) FROM posts WHERE author_id = ?", (user["id"],)
    ).fetchone()[0]
    count_followers = db.execute(
        "SELECT COUNT(*) FROM follows WHERE followed_id = ?", (user["id"],)
    ).fetchone()[0]
    count_following = db.execute(
        "SELECT COUNT(*) FROM follows WHERE follower_id = ?", (user["id"],)
    ).fetchone()[0]
    following = bool(
        db.execute(
            "SELECT 1 FROM follows WHERE follower_id = ? AND followed_id = ?",
            (g.user_id or 0, user["id"]),
        ).fetchone()
    )
    return jsonify(
        user={
            **dict(user),
            "posts": count_posts,
            "followers": count_followers,
            "following": count_following,
            "is_following": following,
        }
    )


@api.post("/users/<username>/follow")
@api.delete("/users/<username>/follow")
def toggle_follow(username):
    viewer, failure = require_user()
    if failure:
        return failure
    db = get_db()
    target = db.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if target is None:
        return error("Пользователь не найден", 404)
    if target["id"] == viewer["id"]:
        return error("Нельзя подписаться на себя")
    with db:
        if request.method == "POST":
            db.execute(
                "INSERT OR IGNORE INTO follows(follower_id, followed_id) VALUES (?, ?)",
                (viewer["id"], target["id"]),
            )
        else:
            db.execute(
                "DELETE FROM follows WHERE follower_id = ? AND followed_id = ?",
                (viewer["id"], target["id"]),
            )
    return jsonify(ok=True)


@api.post("/posts/<int:post_id>/bookmark")
@api.delete("/posts/<int:post_id>/bookmark")
def toggle_bookmark(post_id):
    viewer, failure = require_user()
    if failure:
        return failure
    db = get_db()
    if db.execute("SELECT 1 FROM posts WHERE id = ?", (post_id,)).fetchone() is None:
        return error("Публикация не найдена", 404)
    with db:
        if request.method == "POST":
            db.execute(
                "INSERT OR IGNORE INTO bookmarks(user_id, post_id) VALUES (?, ?)",
                (viewer["id"], post_id),
            )
        else:
            db.execute(
                "DELETE FROM bookmarks WHERE user_id = ? AND post_id = ?",
                (viewer["id"], post_id),
            )
    return jsonify(ok=True)


@api.get("/tags")
def list_tags():
    rows = (
        get_db()
        .execute(
            "SELECT t.name, COUNT(pt.post_id) AS posts FROM tags t JOIN post_tags pt ON pt.tag_id = t.id GROUP BY t.id ORDER BY posts DESC, t.name LIMIT 20"
        )
        .fetchall()
    )
    return jsonify(tags=[dict(row) for row in rows])


@api.get("/health")
def health():
    get_db().execute("SELECT 1").fetchone()
    return jsonify(status="ok")
