# config.py
import os

# --- API Keys (aus Umgebungsvariablen) ---
# Stelle sicher, dass diese Variable gesetzt ist!
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY") 

# --- API Endpoints & Models ---
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL") 

RANDOMUSER_API_URL = "https://randomuser.me/api/"
DUMMYJSON_API_URL = "https://dummyjson.com/users" 
AGIFY_API_URL = "https://api.agify.io/" 

# --- Timeouts & Limits ---
REQUEST_TIMEOUT = 15 
LLM_TIMEOUT = REQUEST_TIMEOUT + 10 # Mehr Zeit für LLM
DUMMYJSON_FETCH_COUNT = 10 
MAX_QUESTIONS_PER_SUSPECT = 10

# --- STT/TTS Konfiguration ---
WHISPER_MODEL_NAME = "base" # "base", "small", "medium", "large" (beeinflusst Download/Performance)
AUDIO_SAMPLE_RATE = 16000
AUDIO_FILENAME = "aufnahme.wav"

# --- Spiel-Logik ---
SUSPICION_THRESHOLD = 3 # Ab wann kommt der "Näherkommen"-Hinweis

# --- Überprüfung wichtiger Konfigurationen ---
def check_config():
    """ Prüft, ob essentielle Konfigurationen vorhanden sind. """
    if not PERPLEXITY_API_KEY:
        print("FATALER FEHLER: Der Perplexity API Key wurde nicht in der Umgebungsvariable 'PERPLEXITY_API_KEY' gefunden.")
        print("Bitte setze die Umgebungsvariable und starte das Skript erneut.")
        import sys
        sys.exit(1) # Beende das Skript, wenn der Key fehlt
    return True

