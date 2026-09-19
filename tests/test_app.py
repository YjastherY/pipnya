import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from app import create_app
from app.db import get_db


class MicroblogTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "test.sqlite3"
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": str(self.database),
                "SECRET_KEY": "test-secret",
            }
        )
        self.alice = self.app.test_client()
        self.bob = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def csrf(self, client):
        return {"X-CSRF-Token": client.get("/api/session").json["csrf_token"]}

    def register(self, client, username):
        return client.post(
            "/api/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "long-password-123",
            },
            headers=self.csrf(client),
        )

    def create_post(self, client, body="Пример заметки", tags=None):
        return client.post(
            "/api/posts",
            json={"body": body, "tags": tags or []},
            headers=self.csrf(client),
        )

    def test_registration_login_and_csrf(self):
        response = self.register(self.alice, "alice")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            self.alice.get("/api/session").json["user"]["username"], "alice"
        )
        duplicate = self.register(self.bob, "Alice")
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(self.alice.post("/api/logout").status_code, 403)
        logout = self.alice.post("/api/logout", headers=self.csrf(self.alice))
        self.assertEqual(logout.status_code, 200)
        denied = self.alice.post(
            "/api/login",
            json={"identity": "alice", "password": "wrong-password"},
            headers=self.csrf(self.alice),
        )
        self.assertEqual(denied.status_code, 401)
        accepted = self.alice.post(
            "/api/login",
            json={"identity": "alice", "password": "long-password-123"},
            headers=self.csrf(self.alice),
        )
        self.assertEqual(accepted.status_code, 200)
        with self.app.app_context():
            saved = (
                get_db()
                .execute("SELECT password_hash FROM users WHERE username = 'alice'")
                .fetchone()[0]
            )
            self.assertNotIn("long-password-123", saved)

    def test_post_crud_search_and_access(self):
        self.register(self.alice, "alice")
        self.register(self.bob, "bobby")
        created = self.create_post(
            self.alice, "Python и базы данных", ["python", "sqlite", "идеи"]
        )
        self.assertEqual(created.status_code, 201)
        post_id = created.json["post"]["id"]
        self.assertEqual(self.bob.get("/api/posts?tag=python").json["total"], 1)
        self.assertEqual(self.bob.get("/api/posts?tag=идеи").json["total"], 1)
        self.assertEqual(self.bob.get("/api/posts?q=%25").json["total"], 0)
        self.assertEqual(self.bob.get("/api/posts?q=базы").json["total"], 1)
        self.assertEqual(
            self.bob.patch(
                f"/api/posts/{post_id}",
                json={"body": "Чужой текст", "tags": []},
                headers=self.csrf(self.bob),
            ).status_code,
            403,
        )
        self.assertEqual(
            self.bob.delete(
                f"/api/posts/{post_id}", headers=self.csrf(self.bob)
            ).status_code,
            403,
        )
        edited = self.alice.patch(
            f"/api/posts/{post_id}",
            json={"body": "Обновлённая заметка", "tags": ["sqlite"]},
            headers=self.csrf(self.alice),
        )
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(self.alice.get("/api/posts?tag=python").json["total"], 0)
        self.assertIsNotNone(edited.json["post"]["updated_at"])
        self.assertEqual(
            self.alice.delete(
                f"/api/posts/{post_id}", headers=self.csrf(self.alice)
            ).status_code,
            200,
        )
        self.assertEqual(self.alice.get("/api/posts").json["total"], 0)

    def test_follows_bookmarks_and_database_constraints(self):
        self.register(self.alice, "alice")
        self.register(self.bob, "bobby")
        post_id = self.create_post(self.alice, "Новая заметка", ["flask"]).json["post"][
            "id"
        ]
        self.assertEqual(self.bob.get("/api/posts?feed=following").json["total"], 0)
        follow = self.bob.post("/api/users/alice/follow", headers=self.csrf(self.bob))
        self.assertEqual(follow.status_code, 200)
        self.assertEqual(self.bob.get("/api/posts?feed=following").json["total"], 1)
        self.assertEqual(
            self.alice.post(
                "/api/users/alice/follow", headers=self.csrf(self.alice)
            ).status_code,
            400,
        )
        self.assertEqual(
            self.bob.post(
                f"/api/posts/{post_id}/bookmark", headers=self.csrf(self.bob)
            ).status_code,
            200,
        )
        self.assertEqual(self.bob.get("/api/posts?feed=saved").json["total"], 1)
        self.assertTrue(
            self.bob.get("/api/posts?feed=saved").json["posts"][0]["bookmarked"]
        )
        self.assertEqual(
            self.bob.delete(
                f"/api/posts/{post_id}/bookmark", headers=self.csrf(self.bob)
            ).status_code,
            200,
        )
        self.assertEqual(self.bob.get("/api/posts?feed=saved").json["total"], 0)
        with self.app.app_context():
            db = get_db()
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "INSERT INTO posts(author_id, body) VALUES (?, ?)",
                    (99999, "orphan"),
                )
            db.rollback()
            self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_database_backup_and_health(self):
        self.register(self.alice, "alice")
        self.create_post(self.alice)
        runner = self.app.test_cli_runner()
        self.assertEqual(runner.invoke(args=["check-db"]).exit_code, 0)
        backup = Path(self.temp.name) / "backup.sqlite3"
        result = runner.invoke(args=["backup-db", str(backup)])
        self.assertEqual(result.exit_code, 0, result.output)
        with closing(sqlite3.connect(backup)) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 1
            )
        self.assertEqual(self.alice.get("/api/health").json["status"], "ok")

    def test_demo_seed_is_repeatable(self):
        runner = self.app.test_cli_runner()
        self.assertNotEqual(
            runner.invoke(args=["seed-demo"], env={"DEMO_PASSWORD": ""}).exit_code, 0
        )
        for _ in range(2):
            result = runner.invoke(
                args=["seed-demo"], env={"DEMO_PASSWORD": "demo-password-123"}
            )
            self.assertEqual(result.exit_code, 0, result.output)
        with self.app.app_context():
            db = get_db()
            self.assertEqual(db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 4)
        response = self.alice.post(
            "/api/login",
            json={"identity": "demo", "password": "demo-password-123"},
            headers=self.csrf(self.alice),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.alice.get("/api/posts?feed=following").json["total"], 2)
        self.assertEqual(self.alice.get("/api/posts?feed=saved").json["total"], 1)

    def test_automatic_demo_seed(self):
        automatic_database = Path(self.temp.name) / "automatic.sqlite3"
        with patch.dict(
            "os.environ",
            {
                "AUTO_SEED_DEMO": "1",
                "DEMO_PASSWORD": "demo-password-123",
            },
        ):
            automatic_app = create_app(
                {
                    "TESTING": True,
                    "DATABASE": str(automatic_database),
                    "SECRET_KEY": "test-secret",
                }
            )
        with automatic_app.app_context():
            db = get_db()
            self.assertEqual(db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM posts").fetchone()[0], 4)


if __name__ == "__main__":
    unittest.main()
