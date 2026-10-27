import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI,HTTPException,status

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
        conn.execute(SCHEMA)
        if conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"] == 0:
            events_to_create = ["Koncert", "Seans filmowy"]
            for event_name in events_to_create:
                event_id = conn.execute(
                    "INSERT INTO events (name) VALUES (%s) RETURNING id",
                    (event_name,)
                ).fetchone()["id"]

                for row in "AB":
                    for number in range(1, 6):
                        conn.execute(
                            "INSERT INTO seats (event_id, label) VALUES (%s, %s)",
                            (event_id, f"{row}{number}"),
                        )

@app.get("/events")
def pokaz_wydarzenia():
    with get_conn() as conn:
        return conn.execute("SELECT id, name FROM events").fetchall()

@app.get("/reservations") #lista zasobów
def pokaz_rezerwacje():
    query = """
        SELECT reservations.id, reservations.email, reservations.created_at, seats.label, events.name
        FROM reservations
        JOIN seats ON reservations.seat_id = seats.id
        JOIN events ON seats.event_id = events.id
        ORDER BY reservations.id ASC
    """
    with get_conn() as conn:
        return conn.execute(query).fetchall()

@app.post("/reservations")
def stworz_rezerwacje(dane: dict):
    if "seat.id" not in dane or "email" not in dane:
        raise HTTPException(status_code=400, detail = "Brak wymaganych pól: seat_id oraz email")
    
    seat_id = dane["seat_id"]
    email = dane["email"]

    if not isinstance(seat_id, int):
        raise HTTPException(status_code=400, detail = "Pole seat_id musi być liczbą całkowitą")

    if not isinstance(email, str) or "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Niepoprawny format adresu e-mail")

    with get_conn() as conn:
        seat = conn.execute(
            "SELECT seats.id FROM seats WHERE seats.id = %s", (seat_id,)).fetchone()

        if seat is None:
            raise HTTPException(status_code=404, detail="Miejsce o podanym ID nie istnieje")

    istniejaca_rezerwacja = conn.execute("SELECT reservations.id FROM reservations WHERE reservations.seat_id = %s",(seat_id,)).fetchone()

    if istniejaca_rezerwacja is not None:
        raise HTTPException(status_code = 400, detail="To miejsce jest juz zarezerwowane")

    nowa_rezerwacja = conn.execute("""
            INSERT INTO reservations (seat_id, email)
            VALUES (%s, %s) RETURNING reservations.id, reservations.seat_id, reservations.email, reservations.created_at
            """, (seat_id, email)
        ).fetchone()

    return nowa_rezerwacja

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
    except Exception:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ok"}
    
