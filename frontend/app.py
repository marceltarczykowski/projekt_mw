import streamlit
import requests
import os

streamlit.title("Rezerwacja biletów")

try:
    response = requests.get(os.environ["BACXKEND_URL"] + "/events", timeout = 5)
    response.raise_for_status()   
    dane_json = response.json()

    streamlit.table(response.json())
        
    
except requests.exceptions.RequestException as e:
    streamlit.error(f"Błąd połączenia: Nie udało się pobrać danych z backendu.\nSzczegóły: {e}")
    
