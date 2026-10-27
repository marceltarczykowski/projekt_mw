import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI,HTTPException

app=FastAPI()


def get_conn():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS seats (
    id SERIAL PRIMARY KEY,
    event_id INT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    UNIQUE (event_id, label)
);
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    seat_id INT NOT NULL UNIQUE REFERENCES seats(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

@app.on_event("startup")
def init_db():
    with get_conn() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, name TEXT)")
        if conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"] == 0:
            conn.execute("INSERT INTO events (name) VALUES ('Koncert'), ('Seans filmowy')")


@app.get("/events")
def pokaz_wydarzenia():
    with get_conn() as conn:
        return conn.execute("SELECT id, name FROM events").fetchall()


@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
    except Exception:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ok"}
    