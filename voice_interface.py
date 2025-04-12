# voice_interface.py
import time
import random
import sounddevice as sd
import numpy as np
import wavio
import whisper
import pyttsx3
from config import AUDIO_SAMPLE_RATE, AUDIO_FILENAME, WHISPER_MODEL_NAME

# --- TTS Setup (unverändert) ---
tts_engine = None
try:
    _engine = pyttsx3.init()
    voices = _engine.getProperty('voices')
    german_voice_found = False
    for voice in voices:
        if "german" in voice.name.lower() or "de-DE" in voice.id or "de_DE" in voice.id:
            _engine.setProperty('voice', voice.id)
            print(f"[TTS] Deutsche Stimme gefunden und gesetzt: {voice.id}")
            german_voice_found = True
            break
    if not german_voice_found:
         print("[TTS] Warnung: Keine spezifisch deutsche Stimme gefunden. Nutze Standardstimme.")
    tts_engine = _engine 
except Exception as e:
    print(f"[TTS] Fehler beim Initialisieren der TTS-Engine: {e}")
    
# --- STT Setup (unverändert) ---
stt_model = None
try:
    print(f"Lade STT-Modell (Whisper '{WHISPER_MODEL_NAME}')...")
    stt_model = whisper.load_model(WHISPER_MODEL_NAME) 
    print("STT-Modell geladen.")
except Exception as e:
    print(f"FEHLER beim Laden des Whisper STT-Modells: {e}")
    # stt_model bleibt None

# --- TTS/STT Funktionen (speak, record_audio, transcribe_audio unverändert) ---
def speak(text):
    """Spricht den übergebenen Text laut aus, wenn TTS verfügbar ist."""
    if tts_engine:
        try:
            text_to_speak = text.replace("*", "").replace("'", "").replace("`", "")
            print(f"[TTS] Spreche: '{text_to_speak[:60]}...'") 
            tts_engine.say(text_to_speak)
            tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"[TTS] Fehler während der Sprachausgabe: {e}")
            print(f"(Fallback-Text): '{text}'") 
            return False
    else:
        print(f"(TTS Deaktiviert): '{text}'")
        return False

def record_audio(seconds=5, fs=AUDIO_SAMPLE_RATE, filename=AUDIO_FILENAME):
    """ Nimmt Audio auf und speichert es. """
    print(f"[STT] Aufnahme startet für {seconds} Sekunden...")
    try:
        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  
        wavio.write(filename, audio, fs, sampwidth=2)
        print(f"[STT] Aufnahme beendet: {filename}")
        return filename
    except Exception as e:
        print(f"[STT] Fehler bei der Audioaufnahme: {e}")
        return None

def transcribe_audio(filename):
    """ Transkribiert Audio mit dem geladenen Whisper-Modell. """
    if not stt_model:
        print("[STT] Fehler: Whisper-Modell nicht geladen.")
        return ""
    if not filename: return ""
    try:
        print("[STT] Transkribiere Audio...")
        result = stt_model.transcribe(filename, language="de", fp16=False) 
        print("[STT] Transkription abgeschlossen.")
        return result["text"].strip()
    except Exception as e:
        print(f"[STT] Fehler bei der Transkription: {e}")
        return ""

# *** Angepasste Funktion für Benutzereingabe ***
def get_user_input(prompt_message="Deine Frage"):
    """ 
    Holt Benutzereingabe entweder per Sprache oder Text.
    Erkennt jetzt auch direkt 'wechseln' oder 'raten' als Texteingabe.
    """
    while True:
        # Frage nach Modus nur, wenn STT verfügbar ist
        if stt_model:
            mode_prompt = f"{prompt_message}? Sprache (s) / Text (t) / Wechseln (w) / Raten (r): "
            mode = input(mode_prompt).strip().lower()
        else: # Wenn kein STT, nur Text oder Befehle möglich
             mode = 't' 
             # Gib Prompt direkt aus, erwarte dann Text oder Befehl
             text_input = input(f"{prompt_message} (Text / 'wechseln' / 'raten'): ").strip()
             # Prüfe auf Befehle zuerst
             if text_input.lower() == 'wechseln': return 'wechseln'
             if text_input.lower() == 'raten': return 'raten'
             # Ansonsten ist es die Frage
             return text_input

        # Verarbeitung, wenn STT verfügbar ist und Modus gewählt wurde
        if mode == "s":
            try:
                duration_input = input("Aufnahme-Dauer in Sekunden (Enter für 5s): ").strip()
                duration = int(duration_input) if duration_input else 5
            except ValueError: duration = 5
            
            audio_file = record_audio(seconds=duration)
            if audio_file:
                text_input = transcribe_audio(audio_file)
                print(f"[STT] Erkannt: '{text_input}'")
                # Keine Bestätigung mehr nötig, User kann 't' wählen wenn STT schlecht ist
                return text_input # Gib erkannten Text zurück
            else:
                print("Aufnahme fehlgeschlagen, bitte Text eingeben."); mode = 't' # Fallback

        if mode == "t":
            # Frage nach Texteingabe
            return input("Deine Frage (Text): ").strip()
        
        # Direkte Befehle als Modus-Eingabe erlauben
        if mode == "w" or mode == "wechseln":
             return "wechseln"
        if mode == "r" or mode == "raten":
             return "raten" 
            
        print("Ungültige Eingabe.")

# Funktion für die finale Beschuldigung (bleibt vorerst Text)
def get_user_accusation_input(possible_secret_types_map):
     """ Holt die Vermutung des Spielers per Text. """
     display_types_list = [f"'{name}'" for name in possible_secret_types_map.values()]
     possible_secrets_display_str = ', '.join(display_types_list)
     
     prompt = f"Deine Vermutung (Tippe einen der Typen oben oder 'nichts'): "
     guess_input_raw = input(prompt).strip()

     # Normalisiere und versuche zuzuordnen
     guess_keyword_normalized = guess_input_raw.lower().replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
     guessed_type = None
     for secret_type_internal, display_name in possible_secret_types_map.items():
          if secret_type_internal in guess_keyword_normalized or display_name.lower().replace(" ", "_") in guess_keyword_normalized:
               guessed_type = secret_type_internal
               break
     if "nichts" in guess_keyword_normalized:
          guessed_type = None 
          
     if guessed_type is None and guess_keyword_normalized not in ['nichts', '']:
          print(f"(Konnte '{guess_input_raw}' keinem Typ zuordnen, werte als falsch)")
          
     return guessed_type # Gibt den internen Typ oder None zurück

