import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI

app=FastAPI()


def get_conn():
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row)


@app.on_event("startup")
def init_db():
    with get_conn() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS events (id SERIAL PRIMARY KEY, name TEXT)")
        if conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"] == 0:
            conn.execute("INSERT INTO events (name) VALUES ('Koncert'), ('Seans filmowy')")


@app.get("/events")
def list_events():
    with get_conn() as conn:
        return conn.execute("SELECT id, name FROM events").fetchall()
    