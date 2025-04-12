# api_clients.py
import requests
import json
import random
from config import (
    RANDOMUSER_API_URL, DUMMYJSON_API_URL, AGIFY_API_URL, 
    REQUEST_TIMEOUT, DUMMYJSON_FETCH_COUNT
)

# --- API Abruf-Funktionen ---
def get_random_user_data():
    """Ruft Daten von randomuser.me ab."""
    try:
        response = requests.get(RANDOMUSER_API_URL, timeout=REQUEST_TIMEOUT) 
        response.raise_for_status() 
        data = response.json()
        if data and 'results' in data and len(data['results']) > 0: return data['results'][0]
        else: print("Fehler: Unerwartetes Datenformat von RandomUser API."); return None
    except requests.exceptions.Timeout: print(f"Fehler: Timeout nach {REQUEST_TIMEOUT}s bei RandomUser."); return None
    except requests.exceptions.RequestException as e: print(f"Fehler beim Abrufen der RandomUser Daten: {e}"); return None
    except json.JSONDecodeError: print("Fehler beim Verarbeiten der JSON-Antwort von RandomUser."); return None

def get_dummy_user_data():
    """Ruft eine Liste von Benutzern von dummyjson.com ab und wählt zufällig einen aus."""
    headers = {'User-Agent': 'DetectiveGameClient/1.0'}
    params = {'limit': DUMMYJSON_FETCH_COUNT} 
    try:
        response = requests.get(DUMMYJSON_API_URL, headers=headers, params=params, timeout=REQUEST_TIMEOUT) 
        response.raise_for_status()
        data = response.json()
        if data and 'users' in data and len(data['users']) > 0: return random.choice(data['users']) 
        else: print(f"Fehler: Unerwartetes Datenformat von DummyJSON."); return None
    except requests.exceptions.Timeout: print(f"Fehler: Timeout nach {REQUEST_TIMEOUT}s bei DummyJSON."); return None
    except requests.exceptions.RequestException as e:
        error_text = f" Status Code: {e.response.status_code}, Response: {e.response.text}" if e.response is not None else ""
        print(f"Fehler beim Abrufen der DummyJSON Daten: {e}{error_text}"); return None
    except json.JSONDecodeError: print("Fehler beim Verarbeiten der JSON-Antwort von DummyJSON."); return None

def get_agify_data(first_name):
    """Ruft die Altersschätzung von Agify.io für einen Vornamen ab."""
    if not first_name: return None
    params = {'name': first_name}
    try:
        response = requests.get(AGIFY_API_URL, params=params, timeout=REQUEST_TIMEOUT) 
        response.raise_for_status(); data = response.json()
        if 'age' in data: return data['age']
        else: return None 
    except requests.exceptions.Timeout: print(f"Fehler: Timeout nach {REQUEST_TIMEOUT}s bei Agify für '{first_name}'."); return None
    except requests.exceptions.RequestException as e: print(f"Fehler beim Abrufen der Agify Daten für '{first_name}': {e}"); return None
    except json.JSONDecodeError: print(f"Fehler beim Verarbeiten der JSON-Antwort von Agify für '{first_name}'."); return None

