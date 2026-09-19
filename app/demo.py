import os
import secrets

import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from .db import get_db


def demo_user(db, username, email, password):
    existing = db.execute(
        "SELECT id, email FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        if existing["email"] != email:
            raise click.ClickException(
                f"Имя {username} уже занято другим пользователем"
            )
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(password), existing["id"]),
        )
        return existing["id"]
    return db.execute(
        "INSERT INTO users(username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, generate_password_hash(password)),
    ).lastrowid


def demo_post(db, author_id, body, tags):
    post = db.execute(
        "SELECT id FROM posts WHERE author_id = ? AND body = ?", (author_id, body)
    ).fetchone()
    if post:
        return post["id"]
    post_id = db.execute(
        "INSERT INTO posts(author_id, body) VALUES (?, ?)", (author_id, body)
    ).lastrowid
    for name in tags:
        db.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (name,))
        db.execute(
            "INSERT INTO post_tags(post_id, tag_id) SELECT ?, id FROM tags WHERE name = ?",
            (post_id, name),
        )
    return post_id


@click.command("seed-demo")
@with_appcontext
def seed_demo_command():
    seed_demo_data(os.environ.get("DEMO_PASSWORD", ""))
    click.echo(
        "Демонстрационные данные готовы. Логин: demo, пароль: значение DEMO_PASSWORD"
    )


def seed_demo_data(password):
    if len(password) < 10:
        raise click.ClickException("Задайте DEMO_PASSWORD длиной не менее 10 символов")
    db = get_db()
    with db:
        demo_id = demo_user(db, "demo", "demo@example.invalid", password)
        guide_id = demo_user(
            db, "guide", "guide@example.invalid", secrets.token_urlsafe(32)
        )
        demo_post(
            db,
            demo_id,
            "Привет! Это Маяк — место для коротких заметок и полезных открытий.",
            ["welcome", "ideas"],
        )
        demo_post(
            db,
            demo_id,
            "Сегодня разбираюсь, как внешние ключи защищают связи в базе данных.",
            ["sqlite", "study"],
        )
        guide_post_id = demo_post(
            db,
            guide_id,
            "Хорошая идея становится лучше, когда ею делятся. Попробуйте подписаться и сохранить эту запись.",
            ["ideas", "tips"],
        )
        demo_post(
            db,
            guide_id,
            "Небольшой проект помогает пройти весь путь: от модели данных до работающего интерфейса.",
            ["project", "study"],
        )
        db.execute(
            "INSERT OR IGNORE INTO follows(follower_id, followed_id) VALUES (?, ?)",
            (demo_id, guide_id),
        )
        db.execute(
            "INSERT OR IGNORE INTO bookmarks(user_id, post_id) VALUES (?, ?)",
            (demo_id, guide_post_id),
        )
