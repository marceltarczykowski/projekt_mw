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


@app.get("/events/{event_id}/seats")
def pokaz_miejsca(event_id: int):
    with get_conn() as conn:
        if not conn.execute("SELECT 1 FROM events WHERE id = %s", (event_id,)).fetchone():
            raise HTTPException(404, "Event not found")
        return conn.execute(
            """
            SELECT s.id, s.label, (r.id IS NOT NULL) AS reserved
            FROM seats s
            LEFT JOIN reservations r ON r.seat_id = s.id
            WHERE s.event_id = %s
            ORDER BY s.id
            """,
            (event_id,),
        ).fetchall()



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

@app.post("/reservations", status_code=201)
def stworz_rezerwacje(dane: dict):
    if "seat_id" not in dane or "email" not in dane:
        raise HTTPException(status_code=400, detail="Brak wymaganych pól: seat_id oraz email")

    seat_id = dane["seat_id"]
    email = dane["email"]

    if not isinstance(seat_id, int):
        raise HTTPException(status_code=400, detail="Pole seat_id musi być liczbą całkowitą")

    if not isinstance(email, str) or "@" not in email or "." not in email:
        raise HTTPException(status_code=400, detail="Niepoprawny format adresu e-mail")

    with get_conn() as conn:
        seat = conn.execute("SELECT id FROM seats WHERE id = %s", (seat_id,)).fetchone()
        if seat is None:
            raise HTTPException(status_code=404, detail="Miejsce o podanym ID nie istnieje")

        istniejaca_rezerwacja = conn.execute(
            "SELECT id FROM reservations WHERE seat_id = %s", (seat_id,)
        ).fetchone()
        if istniejaca_rezerwacja is not None:
            raise HTTPException(status_code=409, detail="To miejsce jest już zarezerwowane")

        
        return conn.execute(
            "INSERT INTO reservations (seat_id, email) VALUES (%s, %s) "
            "RETURNING id, seat_id, email, created_at",
            (seat_id, email),
        ).fetchone()
        
@app.get("/reservations/{reservation_id}") #pojedynczy zasób
def pobierz_id_rezerwacji(reservation_id: int):
    query = """
        SELECT reservations.id, reservations.email, reservations.created_at, seats.label, events.name
        FROM reservations
        JOIN seats ON reservations.seat_id = seats.id
        JOIN events ON seats.event_id = events.id
        WHERE reservations.id = %s
    """
    with get_conn() as conn:
        rezerwacja = conn.execute(query, (reservation_id,)).fetchone()
        if rezerwacja is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rezerwacja o podanym ID nie istnieje"
            )
        return rezerwacja

@app.delete("/reservations/{reservation_id}")
def usun_rezerwacje(reservation_id: int):
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM reservations WHERE id = %s",
            (reservation_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rezerwacja o podanym ID nie istnieje"
            )

        return {"message": "Rezerwacja została usunięta", "id": reservation_id}

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
    except Exception:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ok"}
    
