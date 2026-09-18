CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CHECK (length(username) BETWEEN 3 AND 24)
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT,
    CHECK (length(trim(body)) BETWEEN 1 AND 1000)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    CHECK (length(name) BETWEEN 2 AND 24)
);

CREATE TABLE IF NOT EXISTS post_tags (
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE IF NOT EXISTS follows (
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    followed_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (follower_id, followed_id),
    CHECK (follower_id <> followed_id)
);

CREATE TABLE IF NOT EXISTS bookmarks (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (user_id, post_id)
);

CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_post_tags_tag ON post_tags(tag_id, post_id);
CREATE INDEX IF NOT EXISTS idx_follows_followed ON follows(followed_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_post ON bookmarks(post_id);
