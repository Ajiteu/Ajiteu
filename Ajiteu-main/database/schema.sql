-- Ajiteu ORM(models.py)과 맞는 SQLite 스키마 (참고용)
-- 실제 테이블은 Flask-Migrate: flask db upgrade 로 만듭니다.
-- 수동 적용 예: sqlite3 instance/ajiteu.db < database/schema.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(150) NOT NULL UNIQUE,
  password VARCHAR(200) NOT NULL,
  email VARCHAR(120) NOT NULL UNIQUE,
  nickname VARCHAR(120) NOT NULL,
  user_intro TEXT,
  image_path VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL,
  create_date DATETIME NOT NULL,
  modify_date DATETIME,
  image_path TEXT,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  create_date DATETIME NOT NULL,
  modify_date DATETIME,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reply (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  create_date DATETIME NOT NULL,
  modify_date DATETIME,
  post_id INTEGER,
  comment_id INTEGER,
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
  FOREIGN KEY (comment_id) REFERENCES comment(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS post_liker (
  user_id INTEGER NOT NULL,
  post_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, post_id),
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comment_liker (
  user_id INTEGER NOT NULL,
  comment_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, comment_id),
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  FOREIGN KEY (comment_id) REFERENCES comment(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reply_liker (
  user_id INTEGER NOT NULL,
  reply_id INTEGER NOT NULL,
  PRIMARY KEY (user_id, reply_id),
  FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
  FOREIGN KEY (reply_id) REFERENCES reply(id) ON DELETE CASCADE
);
