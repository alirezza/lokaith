# main.py
import time
import random
import sys

# Importiere aus anderen Modulen
from config import check_config, MAX_QUESTIONS_PER_SUSPECT, SUSPICION_THRESHOLD
from scenario_data import load_scenario 
from llm_interaction import get_perplexity_response
# Importiere spezifische Funktionen aus voice_interface
from voice_interface import speak, get_user_input, get_user_accusation_input 
# Importiere die initialisierten Objekte direkt, wenn sie global in voice_interface sind
# oder initialisiere sie hier, falls sie nicht global sind.
# Annahme: stt_model und tts_engine sind in voice_interface initialisiert und importierbar
from voice_interface import stt_model, tts_engine
from minigames import play_random_minigame

# --- Angepasste Hybrid-Antwort Funktion ---
def get_answer(suspect, question, conversation_history):
    """ 
    Versucht zuerst, die Frage aus bekannten Fakten/Alibi zu beantworten.
    Fällt auf LLM zurück, wenn keine direkte Antwort möglich ist.
    """
    normalized_question = question.lower().strip()
    
    # 1. Prüfe auf einfache Profilfragen
    if "name" in normalized_question or "heißen sie" in normalized_question or "wer sind sie" in normalized_question:
        return f"Mein Name ist {suspect.name}."
    if "alter" in normalized_question or "alt sind sie" in normalized_question:
         return f"Ich bin {suspect.age} Jahre alt."
    if "job" in normalized_question or "arbeit" in normalized_question or "beruf" in normalized_question:
         company = f" bei {suspect.known_facts.get('firma', suspect.job.split(' bei ')[-1])}" if suspect.job else "" # Versucht Firma zu finden
         job_title = suspect.job.split(' bei ')[0] if ' bei ' in suspect.job else suspect.job
         return f"Ich arbeite als {job_title}{company}."
         
    # 2. Prüfe auf Alibi-Fragen (überarbeitet)
    alibi_keywords = ["alibi", "tatzeit", "gestern abend", "wo waren sie", "19 uhr", "20 uhr", "21 uhr", "gemacht"]
    # Prüfe ob *irgendein* Alibi-Keyword vorkommt
    if any(keyword in normalized_question for keyword in alibi_keywords):
         # Gib immer das Alibi zurück, wenn die Frage zeitlich relevant ist
         # Die KI kann dann im nächsten Schritt ggf. Details liefern, wenn weiter gefragt wird
         return f"Gestern Abend zwischen 19 und 21 Uhr? {suspect.alibi}"

    # 3. Prüfe auf bekannte Fakten (Beispiel Anwesenheit)
    if "anwesenheit" in normalized_question and "büro" in normalized_question:
         fact = suspect.known_facts.get("anwesenheit_büro_tatzeit")
         if fact is not None: 
              if isinstance(fact, bool): return "Ja, ich war im Büro." if fact else "Nein, ich war nicht im Büro."
              return str(fact) 
              
    # 4. Wenn keine direkte Antwort -> LLM fragen
    print("[INFO] Frage erfordert Nachdenken... (Rufe LLM)", flush=True) 
    return get_perplexity_response(suspect, question, conversation_history)


# --- Hauptprogramm ---
if __name__ == "__main__":
    print("DEBUG: Skriptstart.", flush=True) 
    print("DEBUG: Prüfe Konfiguration...", flush=True) 
    check_config() 
    print("DEBUG: Konfiguration OK.", flush=True) 
    print(f"DEBUG: STT Modell geladen: {'Ja' if stt_model else 'Nein'}", flush=True) 
    print(f"DEBUG: TTS Engine initialisiert: {'Ja' if tts_engine else 'Nein'}", flush=True) 
    print("DEBUG: Initialisierung abgeschlossen. Lade jetzt Szenario...", flush=True) 

    current_scenario = load_scenario("SPIONAGE01") 
    if not current_scenario:
        print("FEHLER: Szenario konnte nicht geladen werden.", flush=True) 
        sys.exit(1) 
    print("DEBUG: Szenario geladen.", flush=True) 

    print("\n" + "="*30); print("     DETEKTIVSPIEL START"); print("="*30)
    print(f"\n--- Szenario: {current_scenario.title} ---")
    print(current_scenario.description)
    speak(f"Neuer Fall: {current_scenario.title}. {current_scenario.description}")

    interviewed_suspects = {} 
    total_questions_asked = 0 

    # --- Hauptschleife für Verdächtigen-Auswahl ---
    while True: 
        current_scenario.list_suspects()
        speak("Wen möchtest du befragen?")
        
        # *** NEU: Standard input() für ID-Auswahl ***
        suspect_choice_id = input("Wähle die ID des Verdächtigen (oder 'ende' zum Beschuldigen): ").strip().upper()

        if suspect_choice_id == 'ENDE':
            break 

        current_suspect = current_scenario.get_suspect(suspect_choice_id)

        if not current_suspect:
            print("Ungültige Auswahl."); speak("Ungültige Auswahl.")
            continue

        print(f"\n--- Befragung von {current_suspect.name} ---")
        speak(f"Du befragst jetzt {current_suspect.name}.")
        print(current_suspect.get_initial_info())

        conversation_history = interviewed_suspects.get(current_suspect.id, [])
        questions_this_suspect = 0
        suspicion_score = 0 
        suspicion_feedback_given = False

        # --- Innere Schleife für Fragen an aktuellen Verdächtigen ---
        while questions_this_suspect < MAX_QUESTIONS_PER_SUSPECT:
            remaining_q_suspect = MAX_QUESTIONS_PER_SUSPECT - questions_this_suspect
            print(f"\nNoch {remaining_q_suspect} Fragen für {current_suspect.name}.")
            speak(f"Noch {remaining_q_suspect} Fragen für {current_suspect.name}.")

            # *** NEU: get_user_input nutzen, das 'wechseln'/'raten' erkennt ***
            user_input_raw = get_user_input("Deine Frage (oder 'wechseln'/'raten'/'minigame')")
            
            # Befehle zuerst prüfen
            cmd = user_input_raw.lower()
            if cmd == 'wechseln':
                 print("Wechsle Verdächtigen..."); speak("Wechsle Verdächtigen.")
                 break
            if cmd == 'raten':
                 suspect_choice_id = 'ENDE'
                 break
            if cmd == 'minigame' or cmd == 'spiel':
                 won = play_random_minigame()
                 if won:
                     hint = current_scenario.get_bonus_hint()
                     if hint:
                         print(f"[Hinweis] {hint}")
                         speak(hint)
                 continue

            question = user_input_raw # Es ist eine Frage
            if not question: continue
            questions_this_suspect += 1
            total_questions_asked += 1

            # Stress-Indikator & Suspicion Score (unverändert)
            shows_stress = False
            for keyword in current_suspect.keywords: 
                if keyword in question.lower(): 
                    shows_stress = True; suspicion_score += 1; break 
            if shows_stress:
                stress_reactions = ["[INFO] Die Person räuspert sich kurz...", "[INFO] Die Person blickt kurz zur Seite...", "[INFO] Die Person scheint zu zögern...", "[INFO] Ein Zucken im Mundwinkel?"]
                print(random.choice(stress_reactions)); time.sleep(0.4) 

            # Feedback bei hohem Verdacht (unverändert)
            if suspicion_score >= SUSPICION_THRESHOLD and not suspicion_feedback_given:
                 feedback_msg = f"[INFO] Deine Fragen zu diesem Thema scheinen {current_suspect.name} unter Druck zu setzen..."
                 print(feedback_msg); speak(feedback_msg)
                 suspicion_feedback_given = True; time.sleep(0.5)
                
            # *** NEU: Angepasste Hybrid-Antwort holen ***
            answer = get_answer(current_suspect, question, conversation_history)
            
            print(f"\n>> {current_suspect.name} antwortet:")
            print(f"   '{answer}'") 
            speak(answer) 
            
            # Historie aktualisieren (unverändert)
            conversation_history.append({"role": "user", "content": question}) 
            if answer and not answer.startswith("[Fehler"): conversation_history.append({"role": "assistant", "content": answer}) 
            else: conversation_history.append({"role": "assistant", "content": "(Antwort Fehler)"}) 
            
            interviewed_suspects[current_suspect.id] = conversation_history
            time.sleep(0.5) 
            
            if suspect_choice_id == 'ENDE': break 

        if suspect_choice_id == 'ENDE': break 

        if questions_this_suspect == MAX_QUESTIONS_PER_SUSPECT:
             print(f"\nDu hast keine Fragen mehr für {current_suspect.name}.")
             speak(f"Keine Fragen mehr für {current_suspect.name}.")
             
    # --- FINALE BESCHULDIGUNG ---
    print("\n" + "="*30); print("     FINALE BESCHULDIGUNG"); print("="*30)
    speak("Wen beschuldigst du?")
    current_scenario.list_suspects()
    
    # *** NEU: Standard input() für finale Beschuldigung ***
    accusation_id = input("Wähle die ID des Verdächtigen, den du beschuldigst: ").strip().upper()
    
    accused_suspect = current_scenario.get_suspect(accusation_id)
    actual_culprit_id = current_scenario.culprit_id

    print("\n--- Ergebnis ---")
    # (Rest der Ergebnislogik unverändert)
    if accused_suspect and accused_suspect.id == actual_culprit_id:
         result_message = f"Korrekt! {accused_suspect.name} war der Täter.\n"
         result_message += f"Das Motiv/Geheimnis war: {accused_suspect.secret_details}\n"
         result_message += "Fall abgeschlossen! Du hast gewonnen!"
    elif accused_suspect:
         result_message = f"Falsch! {accused_suspect.name} war unschuldig.\n"
         culprit = current_scenario.get_suspect(actual_culprit_id)
         result_message += f"Der wahre Täter war {culprit.name}.\n"
         result_message += f"Dessen Motiv/Geheimnis war: {culprit.secret_details}\n"
         result_message += "Du hast verloren."
    else:
         result_message = "Ungültige Auswahl für die Beschuldigung. Du hast verloren."

    print(result_message)
    speak(result_message) 
            
    print("\nSpiel beendet.")
    speak("Spiel beendet.") 
