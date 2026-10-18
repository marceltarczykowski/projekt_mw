from flask import Flask
import requests
import os

app = Flask(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

@app.route("/")
def index():
    try:
    
        response = requests.get(f"{BACKEND_URL}/")
        response.raise_for_status()
        
        dane_json = response.json()
        
        return f"""
        <h1>Aplikacja Frontendowa</h1>
        <p>Odpowiedz pobrana z backendu:</p>
        <pre>{dane_json}</pre>
        """
    except requests.exceptions.RequestException as e:
        return f"<h1>Blad polaczenia</h1><p>Nie udalo sie pobrac danych z backendu: {e}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)