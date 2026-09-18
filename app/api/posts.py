from flask import g, jsonify, request

from ..db import get_db
from . import api
from .shared import (
    current_user,
    error,
    get_post,
    parse_post,
    payload,
    post_record,
    replace_tags,
    require_user,
)


@api.get("/posts")
def list_posts():
    db = get_db()
    feed = request.args.get("feed", "all")
    if feed not in {"all", "following", "mine", "saved"}:
        return error("Неизвестная лента")
    if feed != "all" and current_user() is None:
        return error("Войдите, чтобы открыть эту ленту", 401)
    try:
        page = int(request.args.get("page", "1"))
    except ValueError:
        return error("Неверный номер страницы")
    if page < 1 or page > 10000:
        return error("Неверный номер страницы")
    query = request.args.get("q", "").strip()
    tag = request.args.get("tag", "").strip().lower()
    author = request.args.get("author", "").strip()
    if len(query) > 100 or len(tag) > 24 or len(author) > 24:
        return error("Слишком длинный параметр поиска")
    where = []
    args = []
    if feed == "following":
        where.append(
            "EXISTS(SELECT 1 FROM follows f WHERE f.followed_id = p.author_id AND f.follower_id = ?)"
        )
        args.append(g.user_id)
    elif feed == "mine":
        where.append("p.author_id = ?")
        args.append(g.user_id)
    elif feed == "saved":
        where.append(
            "EXISTS(SELECT 1 FROM bookmarks b WHERE b.post_id = p.id AND b.user_id = ?)"
        )
        args.append(g.user_id)
    if author:
        where.append("u.username = ?")
        args.append(author)
    if query:
        escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        where.append("(p.body LIKE ? ESCAPE '\\' OR u.username LIKE ? ESCAPE '\\')")
        args.extend((f"%{escaped}%", f"%{escaped}%"))
    if tag:
        where.append(
            "EXISTS(SELECT 1 FROM post_tags pt JOIN tags t ON t.id = pt.tag_id WHERE pt.post_id = p.id AND t.name = ?)"
        )
        args.append(tag)
    clause = " WHERE " + " AND ".join(where) if where else ""
    source = " FROM posts p JOIN users u ON u.id = p.author_id"
    total = db.execute("SELECT COUNT(*)" + source + clause, args).fetchone()[0]
    rows = db.execute(
        "SELECT p.id, p.author_id, p.body, p.created_at, p.updated_at, u.username, "
        "EXISTS(SELECT 1 FROM bookmarks b WHERE b.post_id = p.id AND b.user_id = ?) AS bookmarked"
        + source
        + clause
        + " ORDER BY p.created_at DESC, p.id DESC LIMIT 10 OFFSET ?",
        [g.user_id or 0, *args, (page - 1) * 10],
    ).fetchall()
    return jsonify(
        posts=[post_record(row, db) for row in rows],
        total=total,
        page=page,
        pages=(total + 9) // 10,
    )


@api.post("/posts")
def create_post():
    user, failure = require_user()
    if failure:
        return failure
    body, tags, message = parse_post(payload())
    if message:
        return error(message)
    db = get_db()
    with db:
        cursor = db.execute(
            "INSERT INTO posts(author_id, body) VALUES (?, ?)", (user["id"], body)
        )
        replace_tags(db, cursor.lastrowid, tags)
    return jsonify(post=get_post(db, cursor.lastrowid, user["id"])), 201


@api.patch("/posts/<int:post_id>")
def edit_post(post_id):
    user, failure = require_user()
    if failure:
        return failure
    db = get_db()
    post = db.execute("SELECT author_id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        return error("Публикация не найдена", 404)
    if post["author_id"] != user["id"]:
        return error("Можно изменять только свои публикации", 403)
    body, tags, message = parse_post(payload())
    if message:
        return error(message)
    with db:
        db.execute(
            "UPDATE posts SET body = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now') WHERE id = ?",
            (body, post_id),
        )
        replace_tags(db, post_id, tags)
    return jsonify(post=get_post(db, post_id, user["id"]))


@api.delete("/posts/<int:post_id>")
def delete_post(post_id):
    user, failure = require_user()
    if failure:
        return failure
    db = get_db()
    post = db.execute("SELECT author_id FROM posts WHERE id = ?", (post_id,)).fetchone()
    if post is None:
        return error("Публикация не найдена", 404)
    if post["author_id"] != user["id"]:
        return error("Можно удалить только свои публикации", 403)
    with db:
        db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    return jsonify(ok=True)
