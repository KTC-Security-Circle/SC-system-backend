import sqlite3

conn = sqlite3.connect('test.db')
cur = conn.cursor()

# 複数のテーブルを作成するSQL文をセミコロンで区切ります
cur.executescript("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    authority TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chatlog (
    id INTEGER PRIMARY KEY,
    message TEXT NOT NULL,
    bot_reply TEXT NOT NULL,
    pub_data TEXT NOT NULL,
    session_id INTEGER
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    session_name TEXT NOT NULL,
    pub_data TEXT NOT NULL,
    user_id INTEGER
);

CREATE TABLE IF NOT EXISTS errorlog (
    id INTEGER PRIMARY KEY,
    error_message TEXT NOT NULL,
    pub_data TEXT NOT NULL,
    session_id INTEGER
);
""")
conn.commit()
conn.close()
