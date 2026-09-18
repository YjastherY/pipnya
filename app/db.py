import sqlite3
from contextlib import closing
from pathlib import Path

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        g.db = connection
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    get_db().executescript(schema)
    get_db().commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("База данных готова")


@click.command("check-db")
@with_appcontext
def check_db_command():
    result = get_db().execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = get_db().execute("PRAGMA foreign_key_check").fetchall()
    if result != "ok" or foreign_keys:
        raise click.ClickException(
            f"Проверка не пройдена: {result}; внешние ключи: {len(foreign_keys)}"
        )
    click.echo("Целостность базы данных подтверждена")


@click.command("backup-db")
@click.argument("destination", type=click.Path(dir_okay=False, path_type=Path))
@with_appcontext
def backup_db_command(destination):
    source = Path(current_app.config["DATABASE"]).resolve()
    destination = destination.resolve()
    if destination == source:
        raise click.ClickException("Укажите другой путь для резервной копии")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(destination)) as backup:
        get_db().backup(backup)
    click.echo(f"Резервная копия создана: {destination}")


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(check_db_command)
    app.cli.add_command(backup_db_command)
