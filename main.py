import requests
import json 
import time
import os 
import random 
# Imports für STT/TTS
import sounddevice as sd
import numpy as np
import wavio
import whisper
import pyttsx3
import sys 

# --- Konfiguration ---
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY") 
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar" 

RANDOMUSER_API_URL = "https://randomuser.me/api/"
DUMMYJSON_API_URL = "https://dummyjson.com/users" 
AGIFY_API_URL = "https://api.agify.io/" 
REQUEST_TIMEOUT = 15 
DUMMYJSON_FETCH_COUNT = 10 
# NEU: Schwellenwert für "Näherkommen"-Hinweis
SUSPICION_THRESHOLD = 3 

# --- TTS Setup ---
try:
    tts_engine = pyttsx3.init()
    voices = tts_engine.getProperty('voices')
    german_voice_found = False
    for voice in voices:
        if "german" in voice.name.lower() or "de-DE" in voice.id or "de_DE" in voice.id:
            tts_engine.setProperty('voice', voice.id)
            print(f"[TTS] Deutsche Stimme gefunden und gesetzt: {voice.id}")
            german_voice_found = True
            break
    if not german_voice_found:
         print("[TTS] Warnung: Keine spezifisch deutsche Stimme gefunden. Nutze Standardstimme.")
except Exception as e:
    print(f"[TTS] Fehler beim Initialisieren der TTS-Engine: {e}")
    tts_engine = None 

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

# --- STT-Funktionen mittels Whisper ---
def record_audio(seconds=5, fs=16000, filename="aufnahme.wav"):
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

def transcribe_audio(filename, model):
    """ Transkribiert Audio mit Whisper. """
    if not filename: return ""
    try:
        print("[STT] Transkribiere Audio...")
        if not isinstance(model, whisper.Whisper):
             print("[STT] Lade Whisper-Modell...")
             model = whisper.load_model(model) 
             print("[STT] Whisper-Modell geladen.")
        result = model.transcribe(filename, language="de", fp16=False) 
        print("[STT] Transkription abgeschlossen.")
        return result["text"].strip()
    except Exception as e:
        print(f"[STT] Fehler bei der Transkription: {e}")
        return ""

# --- Angepasste Funktion für Benutzereingabe ---
def get_user_input(stt_model, prompt_message="Deine Frage"):
    """ Holt Benutzereingabe entweder per Sprache oder Text. """
    while True:
        # Frage immer zuerst nach dem Modus, falls STT verfügbar ist
        if stt_model:
            mode = input(f"{prompt_message}? Sprache (s) / Text (t): ").strip().lower()
        else: # Wenn kein STT, direkt Texteingabe
             mode = 't' 
             print(f"{prompt_message} (Text): ", end='') # Zeige Prompt vor Texteingabe

        if mode == "s" and stt_model:
            try:
                duration_input = input("Aufnahme-Dauer in Sekunden (Enter für 5s): ").strip()
                duration = int(duration_input) if duration_input else 5
            except ValueError: duration = 5
            
            audio_file = record_audio(seconds=duration)
            if audio_file:
                text_input = transcribe_audio(audio_file, stt_model)
                print(f"[STT] Erkannt: '{text_input}'")
                confirm = input("Ist das korrekt? (j/n): ").strip().lower()
                if confirm == 'j' or confirm == '': return text_input # Gib erkannten Text zurück
                else: print("Okay, versuche es nochmal."); continue # Neue Eingabeaufforderung
            else:
                print("Aufnahme fehlgeschlagen, bitte Text eingeben."); mode = 't' # Fallback

        if mode == "t":
            return input().strip() # Lies Texteingabe nach dem Prompt oben
            
        print("Ungültige Eingabe.")

# --- API Abruf-Funktionen (unverändert) ---
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

# --- Perplexity Funktion (unverändert) ---
def get_perplexity_response(persona_profile, user_question, conversation_history):
    """ Sendet die Frage an die Perplexity API und erhält eine Antwort im Charakter der Persona. """
    if not PERPLEXITY_API_KEY: return "[Fehler: Perplexity API Key fehlt - Antwort nicht verfügbar]" 
    system_prompt = f"""Du bist eine KI, die eine fiktive Person spielt. Antworte auf Fragen eines Detektivs auf Deutsch. Bleibe im Charakter basierend auf diesem Profil:
- Name: {persona_profile.get('name_title')} {persona_profile.get('name_first')} {persona_profile.get('name_last')}
- Alter: {persona_profile.get('age_randomuser')}
- Geschlecht: {persona_profile.get('gender')}
- Job: {persona_profile.get('job_title')} bei {persona_profile.get('company_name')}
- Wohnort: {persona_profile.get('city_randomuser')}, {persona_profile.get('country_randomuser')} 
- Universität: {persona_profile.get('university')}
"""
    secret_type = persona_profile.get('secret_narrative_type')
    secret_details = persona_profile.get('secret_narrative_details')
    if secret_type and secret_details:
        system_prompt += f"\nWICHTIGES GEHEIMNIS:\n- DEIN GEHEIMNIS ({secret_type}): {secret_details}\n"
        system_prompt += "- ANWEISUNG: Dies ist dein Geheimnis. Wenn der Detektiv Fragen stellt, die dieses Geheimnis berühren könnten, musst du lügen, ausweichen, vage sein oder das Thema wechseln. Gib das Geheimnis unter keinen Umständen zu! Antworte ansonsten konsistent mit deinem Profil.\n"
    else: system_prompt += "\n- Es gibt kein spezifisches Geheimnis zu verbergen. Antworte ehrlich und konsistent basierend auf deinem Profil.\n"
    system_prompt += "\nAntworte immer kurz und natürlich auf Deutsch."
    messages = [{"role": "system", "content": system_prompt}]
    for entry in conversation_history:
         role = entry.get('role'); content = entry.get('content') or (entry.get('parts')[0] if isinstance(entry.get('parts'), list) and entry.get('parts') else '') 
         if role == 'model': role = 'assistant' 
         if role in ['user', 'assistant'] and content: messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_question})
    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}
    payload = { "model": PERPLEXITY_MODEL, "messages": messages, }
    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT + 5) 
        response.raise_for_status(); api_response_data = response.json()
        if api_response_data and 'choices' in api_response_data and len(api_response_data['choices']) > 0:
            assistant_message = api_response_data['choices'][0].get('message', {}).get('content')
            if assistant_message: return assistant_message.strip()
            else: print("   [API Call] Perplexity ERROR: Keine Antwort im erwarteten Format.")
        else: print("   [API Call] Perplexity ERROR: Unerwartetes Antwortformat.")
        return "[Fehler: Konnte keine gültige Antwort von Perplexity extrahieren]"
    except requests.exceptions.Timeout: print(f"   [API Call] Perplexity ERROR: Timeout nach {REQUEST_TIMEOUT + 5}s."); return "[Fehler: Zeitüberschreitung bei der Anfrage an Perplexity]"
    except requests.exceptions.RequestException as e:
        error_text = f" Status Code: {e.response.status_code}, Response: {e.response.text}" if e.response is not None else ""
        print(f"   [API Call] Perplexity ERROR: {e}{error_text}"); return f"[Fehler bei der Anfrage an Perplexity: {e}]"
    except json.JSONDecodeError: print("   [API Call] Perplexity ERROR: JSON Decode Error."); return "[Fehler beim Verarbeiten der Perplexity JSON-Antwort]"


# --- Hauptprogramm ---
if __name__ == "__main__":
    if not PERPLEXITY_API_KEY:
        print("FEHLER: Der Perplexity API Key wurde nicht in der Umgebungsvariable 'PERPLEXITY_API_KEY' gefunden.")
        sys.exit(1) 

    stt_model = None
    whisper_model_name = "base" 
    try:
        print(f"Lade STT-Modell (Whisper '{whisper_model_name}')...")
        stt_model = whisper.load_model(whisper_model_name) 
        print("STT-Modell geladen.")
    except Exception as e:
        print(f"FEHLER beim Laden des Whisper STT-Modells: {e}")
        print("Fahre im reinen Textmodus fort."); tts_engine = None 

    print("\nRufe Profildaten ab...")
    random_user_profile = get_random_user_data()
    dummy_user_profile = get_dummy_user_data() 
    agify_age = None
    if random_user_profile:
        first_name = random_user_profile.get('name', {}).get('first')
        if first_name: agify_age = get_agify_data(first_name)

    if random_user_profile and dummy_user_profile:
        persona_profile = {}
        # --- Profil füllen ---
        name_data = random_user_profile.get('name', {})
        persona_profile['name_title'] = name_data.get('title')
        persona_profile['name_first'] = name_data.get('first')
        persona_profile['name_last'] = name_data.get('last')
        persona_profile['gender'] = random_user_profile.get('gender')
        persona_profile['age_randomuser'] = random_user_profile.get('dob', {}).get('age')
        persona_profile['email'] = random_user_profile.get('email')
        persona_profile['username'] = random_user_profile.get('login', {}).get('username')
        loc_ru = random_user_profile.get('location', {})
        persona_profile['city_randomuser'] = loc_ru.get('city')
        persona_profile['country_randomuser'] = loc_ru.get('country')
        persona_profile['picture_url'] = random_user_profile.get('picture', {}).get('large')
        company_data = dummy_user_profile.get('company', {})
        address_data = dummy_user_profile.get('address', {})
        persona_profile['company_name'] = company_data.get('name')
        persona_profile['job_title'] = company_data.get('title')
        persona_profile['department'] = company_data.get('department')
        persona_profile['address_dummy'] = address_data.get('address')
        persona_profile['postal_code_dummy'] = address_data.get('postalCode')
        persona_profile['city_dummyjson'] = address_data.get('city') 
        persona_profile['university'] = dummy_user_profile.get('university')
        persona_profile['phone'] = dummy_user_profile.get('phone')
        persona_profile['age_agify'] = agify_age

        # --- Zufälliges Narratives Geheimnis auswählen ---
        possible_secrets = [
             { "type": "activity_yesterday", "details": "...", "keywords": [...] },
             { "type": "job_satisfaction", "details": "...", "keywords": [...] },
             { "type": "hobby_skill", "details": "...", "keywords": [...] },
             { "type": "relationship_status", "details": "...", "keywords": [...] },
             { "type": "fake_trip", "details": "...", "keywords": [...] }
        ] # Details und Keywords wie im vorherigen Codeblock
        # (Code zum Befüllen der Details und Keywords hier eingefügt)
        for secret in possible_secrets:
             if secret["type"] == "job_satisfaction":
                  secret["details"] = secret["details"].format(
                       job=persona_profile.get('job_title', 'Angestellter'), 
                       company=persona_profile.get('company_name', 'einer Firma')
                  )
                  secret["keywords"] = ["job", "arbeit", "chef", "kollegen", "firma", "zufrieden", "spaß", "stress", "wechseln", "neu", "karriere", "gehalt"]
             elif secret["type"] == "fake_trip":
                  possible_cities = ["Paris", "Rom", "Barcelona", "Prag", "Amsterdam", "Wien"]
                  if persona_profile.get('city_randomuser') in possible_cities: possible_cities.remove(persona_profile.get('city_randomuser'))
                  if persona_profile.get('city_dummyjson') in possible_cities: possible_cities.remove(persona_profile.get('city_dummyjson'))
                  fake_city = random.choice(possible_cities) if possible_cities else "einer anderen Stadt"
                  secret["details"] = "Du hast allen erzählt, du wärst letztes Wochenende auf einem spannenden Kurztrip in {city} gewesen. In Wahrheit warst du krank zu Hause und hast die Fotos von einem alten Urlaub gepostet.".replace("{city}", fake_city)
                  secret["keywords"] = ["reise", "trip", "urlaub", "wochenende", "verreist", "stadt", "sehen", "erlebt", fake_city.lower()]
             elif secret["type"] == "activity_yesterday":
                  secret["details"] = "Du warst gestern Abend auf einer lauten WG-Party bis spät in die Nacht, obwohl du eigentlich lernen wolltest. Du behauptest aber gegenüber dem Detektiv, du hättest den ganzen Abend zuhause ein Fachbuch gelesen."
                  secret["keywords"] = ["gestern", "abend", "nacht", "party", "lesen", "buch", "gelesen", "laut", "ruhig", "getan", "gemacht", "gelernt", "feiern"]
             elif secret["type"] == "hobby_skill":
                  secret["details"] = "Du gibst an, ein begeisterter Hobby-Fotograf zu sein. In Wahrheit hast du deine teure Kamera seit über einem Jahr nicht mehr benutzt und deine letzten 'Meisterwerke' waren Handy-Schnappschüsse."
                  secret["keywords"] = ["hobby", "freizeit", "foto", "kamera", "fotografieren", "bilder", "ausrüstung", "objektiv", "leidenschaft"]
             elif secret["type"] == "relationship_status":
                  secret["details"] = "Du erzählst allen, du seist glücklich Single. In Wahrheit hast du seit kurzem eine heimliche Affäre mit einer Person, von der niemand etwas wissen darf."
                  secret["keywords"] = ["beziehung", "freundin", "freund", "partner", "single", "vergeben", "dating", "liebe", "affäre", "zusammen"]


        selected_secret = random.choice(possible_secrets)
        persona_profile['secret_narrative_type'] = selected_secret["type"]
        persona_profile['secret_narrative_details'] = selected_secret["details"]
        secret_keywords = selected_secret["keywords"] 

        print(f"\n[DEBUG] Geheimnis für diese Runde: {persona_profile['secret_narrative_type']}")

        # --- Spiel Start ---
        print("\n" + "="*30); print("     DETEKTIVSPIEL START"); print("="*30)
        # (Startbeschreibung, Hinweis etc. wie zuvor)
        start_message = f"""Du sitzt einer Person gegenüber. Dein erster Eindruck:
  Name: {persona_profile.get('name_title')} {persona_profile.get('name_first')} {persona_profile.get('name_last')}
  Alter (ca.): {persona_profile.get('age_randomuser')}
  Job: {persona_profile.get('job_title', 'Unbekannt')} bei {persona_profile.get('company_name', 'Unbekannt')}
  Wohnort (laut einer Quelle): {persona_profile.get('city_randomuser', 'Unbekannt')}, {persona_profile.get('country_randomuser', 'Unbekannt')}"""
        print(start_message)
        appearance_descriptions = [
            "Die Person wirkt ruhig und gefasst.", "Ein prüfender Blick mustert dich.",
            "Die Person scheint leicht nervös zu sein und zupft an ihrer Kleidung.",
            "Ein freundliches Lächeln liegt auf den Lippen der Person.",
            "Die Person macht einen müden, aber konzentrierten Eindruck.",
            "Ein selbstsicheres Auftreten zeichnet die Person aus.",
        ]
        appearance = f"  Auftreten: {random.choice(appearance_descriptions)}"
        print(appearance)
        clue_map = {
            "activity_yesterday": "Du hast gehört, dass die Person gestern Abend vielleicht doch nicht so einen ruhigen Abend hatte...",
            "job_satisfaction": "Es gibt Gerüchte, dass die Person mit ihrer aktuellen Arbeitssituation nicht ganz glücklich sein könnte.",
            "hobby_skill": "Du fragst dich, ob die Person ihr angegebenes Hobby wirklich so intensiv betreibt...",
            "relationship_status": "Etwas an der Art, wie die Person über ihr Privatleben spricht, kommt dir seltsam vor.",
            "fake_trip": "Die Erzählungen der Person über eine kürzliche Reise klangen fast zu perfekt."
        }
        starting_clue = clue_map.get(persona_profile['secret_narrative_type'], "") 
        if starting_clue: print(f"\n[DEIN HINWEIS] {starting_clue}") 
        print("\n--- Das Interview beginnt ---")
        speak("Das Interview beginnt.") 

        # --- Spiel-Loop mit TTS/STT ---
        max_questions = 10
        questions_asked = 0
        conversation_history = [] 
        # *** NEU: Suspicion Score ***
        suspicion_score = 0
        suspicion_feedback_given = False # Damit der Hinweis nur einmal kommt

        while questions_asked < max_questions:
            remaining_questions = max_questions - questions_asked
            print(f"\nDu hast noch {remaining_questions} Fragen übrig.")
            speak(f"Du hast noch {remaining_questions} Fragen.") 

            # *** NEU: get_user_input statt get_user_question ***
            # (get_user_question wurde umbenannt und leicht angepasst)
            user_input_text = get_user_input(stt_model, prompt_message="Deine Frage") 
            
            # Prüfe, ob der User direkt raten will (aus alter Funktion übernommen)
            if user_input_text.lower() == 'raten':
                 break 
            
            question = user_input_text # Die eigentliche Frage
            if not question: continue
            questions_asked += 1
            
            # Stress-Indikator & Suspicion Score
            shows_stress = False
            for keyword in secret_keywords: 
                if keyword in question.lower(): 
                    shows_stress = True
                    # *** NEU: Suspicion Score erhöhen ***
                    suspicion_score += 1
                    break 
            if shows_stress:
                stress_reactions = ["[INFO] Die Person räuspert sich kurz...", "[INFO] Die Person blickt kurz zur Seite...", "[INFO] Die Person scheint zu zögern...", "[INFO] Ein Zucken im Mundwinkel?"]
                print(random.choice(stress_reactions)); time.sleep(0.4) 

            # *** NEU: Feedback bei hohem Verdacht ***
            if suspicion_score >= SUSPICION_THRESHOLD and not suspicion_feedback_given:
                 feedback_msg = "[INFO] Du scheinst der Sache näher zu kommen..."
                 print(feedback_msg)
                 speak(feedback_msg)
                 suspicion_feedback_given = True # Nur einmal anzeigen
                 time.sleep(0.5)
                
            # Perplexity API aufrufen
            ai_answer = get_perplexity_response(persona_profile, question, conversation_history)
            
            print(f"\n>> {persona_profile.get('name_first', 'Die Person')} antwortet:")
            print(f"   '{ai_answer}'") 
            speak(ai_answer) 
            
            conversation_history.append({"role": "user", "content": question}) 
            if ai_answer and not ai_answer.startswith("[Fehler"): conversation_history.append({"role": "assistant", "content": ai_answer}) 
            else: conversation_history.append({"role": "assistant", "content": "(Antwort Fehler)"}) 
            time.sleep(0.5) 

        # --- Auflösungs-Phase (Mit korrigiertem Input für Vermutung) ---
        print("\n--- Zeit zur Auflösung! ---"); speak("Zeit zur Auflösung.") 
        if questions_asked == max_questions: print("Du hast keine Fragen mehr übrig.")
        
        possible_secret_types = [s['type'] for s in possible_secrets]
        display_type_map = {
             "activity_yesterday": "Aktivität Gestern", "job_satisfaction": "Job Zufriedenheit",
             "hobby_skill": "Hobby/Fähigkeit", "relationship_status": "Beziehungsstatus", "fake_trip": "Reise"
        }
        display_types_list = [f"'{display_type_map.get(t, t)}'" for t in possible_secret_types]
        possible_secrets_display_str = ', '.join(display_types_list)

        print("\nWas glaubst du, war das Geheimnis oder die Lüge?")
        speak("Was glaubst du, war das Geheimnis?") 
        print(f"Mögliche Arten: {possible_secrets_display_str}, 'nichts'")
        
        # *** KORRIGIERTER INPUT FÜR VERMUTUNG ***
        speak("Sage oder tippe deine Vermutung.")
        # Nutze die angepasste get_user_input Funktion
        guess_input_raw = get_user_input(stt_model, prompt_message="Deine Vermutung (Stichwort)")
        
        # Normalisiere und versuche zuzuordnen
        guess_keyword_normalized = guess_input_raw.lower().replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        guessed_type = None
        for secret_type_internal, display_name in display_type_map.items():
             if secret_type_internal in guess_keyword_normalized or display_name.lower().replace(" ", "_") in guess_keyword_normalized:
                  guessed_type = secret_type_internal
                  break
        if "nichts" in guess_keyword_normalized: guessed_type = None 
        
        # Fallback, falls Zuordnung fehlschlägt (optional)
        if guessed_type is None and guess_keyword_normalized != 'nichts':
             print(f"(Konnte '{guess_input_raw}' keinem Typ zuordnen, werte als falsch)")


        actual_secret_type = persona_profile.get('secret_narrative_type')

        print("\n--- Ergebnis ---")
        guessed_correctly = (guessed_type == actual_secret_type)

        result_message = ""
        # (Rest der Ergebnislogik unverändert)
        if guessed_correctly:
             if actual_secret_type is None: result_message = "Korrekt! Es gab kein Geheimnis zu finden."
             else:
                 result_message = f"Volltreffer! Du hast das richtige Thema ({display_type_map.get(actual_secret_type, actual_secret_type)}) erraten!\n"
                 result_message += f"Die Details des Geheimnisses waren: {persona_profile.get('secret_narrative_details')}\n"
             result_message += "Du hast gewonnen!"
        else:
             result_message = "Leider falsch.\n"
             if actual_secret_type is None: result_message += "Es gab kein Geheimnis zu finden."
             else:
                 result_message += f"Das tatsächliche Geheimnis war vom Typ: {display_type_map.get(actual_secret_type, actual_secret_type)}\n"
                 result_message += f"Die Details waren: {persona_profile.get('secret_narrative_details')}"
             result_message += "\nDu hast verloren."
             
        print(result_message)
        speak(result_message) 
            
    else:
        print("\nKonnte nicht alle notwendigen Profildaten für die Persona abrufen. Spiel kann nicht gestartet werden.")

    print("\nSpiel beendet.")
    speak("Spiel beendet.") 

