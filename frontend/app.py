import streamlit as st
import requests
import os

st.title("Rezerwacja biletów")

if "komunikat" in st.session_state:
    st.success(st.session_state.pop("komunikat"))

try:
    response = requests.get(os.environ["BACKEND_URL"] + "/events", timeout = 5)
    response.raise_for_status()   

    st.table(response.json())
    event = st.selectbox("Wydarzenie", response.json(), format_func=lambda e: e["name"]) 
    seats = requests.get(f"{os.environ['BACKEND_URL']}/events/{event['id']}/seats", timeout=5).json()
except requests.exceptions.RequestException as e:
    st.error(f"Błąd połączenia: Nie udało się pobrać danych z backendu.\nSzczegóły: {e}")

st.table([
    {"Miejsce": s["label"], "Status": "zajęte" if s["reserved"] else "wolne"}
    for s in seats
])


free = [s for s in seats if not s["reserved"]]
if not free:
    st.info("Brak wolnych miejsc")
else:
    seat = st.selectbox("Wybierz miejsce", free, format_func=lambda s: s["label"])
    email = st.text_input("E-mail")

    if st.button("Zarezerwuj"):
        r = requests.post(
            f"{os.environ['BACKEND_URL']}/reservations",
            json={"seat_id": seat["id"], "email": email},
            timeout=5,
        )
        if r.status_code == 201:
            st.session_state["komunikat"] = (
                f"Zarezerwowano miejsce {seat['label']} (nr rezerwacji {r.json()['id']})"
            )
            st.rerun()
        elif r.status_code in (400, 404, 409):
            st.error(r.json().get("detail", "Błąd rezerwacji"))
        else:
            st.error("Błąd rezerwacji")