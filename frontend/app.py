import streamlit as st
import requests
import os

st.title("Rezerwacja biletów")

try:
    response = requests.get(os.environ["BACKEND_URL"] + "/events", timeout = 5)
    response.raise_for_status()   

    st.table(response.json())
    event = st.selectbox("Wydarzenie", response.json(), format_func=lambda e: e["name"]) 
    
except requests.exceptions.RequestException as e:
    st.error(f"Błąd połączenia: Nie udało się pobrać danych z backendu.\nSzczegóły: {e}")
    
