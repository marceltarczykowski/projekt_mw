# projekt_mw
Temat projektu to Rezerwacja miejsc/biletów

### GET /health

Odpowiedź 200:

```json
{"status": "ok"}
```

Odpowiedź 503 (brak połączenia z bazą):

```json
{"detail": "Database unavailable"}
```

### GET /events

Odpowiedź 200:

```json
[
  {"id": 1, "name": "Koncert"},
  {"id": 2, "name": "Seans filmowy"}
]
```

### GET /events/{event_id}/seats

Odpowiedź 200 (`reserved` mówi, czy miejsce jest zajęte):

```json
[
  {"id": 1, "label": "A1", "reserved": false},
  {"id": 2, "label": "A2", "reserved": true}
]
```

Odpowiedź 404, gdy wydarzenie nie istnieje:

```json
{"detail": "Event not found"}
```

### GET /reservations

Odpowiedź 200:

```json
[{"id":2,"email":"aaa@wp.pl","created_at":"2026-10-31T15:47:30.865959+00:00","label":"A2","name":"Koncert"}]
```

Pola: `id` (numer rezerwacji), `email`, `created_at` (data utworzenia),
`label` (oznaczenie miejsca), `name` (nazwa wydarzenia).

### GET /reservations/{reservation_id}

Odpowiedź 200 (te same pola co element listy powyżej):

```json
{"id":2,"email":"aaa@wp.pl","created_at":"2026-10-31T15:47:30.865959+00:00","label":"A2","name":"Koncert"}
```

Odpowiedź 404:

```json
{"detail": "Rezerwacja o podanym ID nie istnieje"}
```

### POST /reservations

Żądanie:

```json
{"seat_id": 3, "email": "jan@example.com"}
```
|

Odpowiedź 201:

```json
{
  "id": 1,
  "seat_id": 3,
  "email": "jan@example.com",
  "created_at": "2026-11-04T21:20:00.123456Z"
}
```

Błędy:

| Kod | Kiedy | Przykład `detail` |
|---|---|---|
| 400 | brak pola, `seat_id` nie jest liczbą, niepoprawny e-mail | `Niepoprawny format adresu e-mail` |
| 404 | miejsce o podanym id nie istnieje | `Miejsce o podanym ID nie istnieje` |
| 409 | miejsce jest już zarezerwowane | `To miejsce jest już zarezerwowane` |

### DELETE /reservations/{reservation_id}

Odpowiedź 200:

```json
{"message": "Rezerwacja została usunięta", "id": 1}
```

Odpowiedź 404:

```json
{"detail": "Rezerwacja o podanym ID nie istnieje"}
```

### Inne błędy

Gdy identyfikator w ścieżce nie jest liczbą (np. `/reservations/abc`) albo ciało
żądania nie jest obiektem JSON, FastAPI zwraca standardowy kod 422.