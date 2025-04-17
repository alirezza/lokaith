# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS 
import random # Für Herzschlag-Zufall

# Importiere Logik aus unseren anderen Modulen
from scenario_data import load_scenario, get_available_scenarios, Suspect
from llm_interaction import get_perplexity_response
from config import check_config, MAX_QUESTIONS_PER_SUSPECT, SUSPICION_THRESHOLD

# --- Flask App initialisieren ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 

# --- Spielzustand (vereinfacht für einen Spieler) ---
# ACHTUNG: Globale Variablen sind NICHT geeignet für mehrere gleichzeitige Benutzer!
game_state = {
    "current_scenario_id": None,
    "current_scenario": None,
    "interview_states": {} # Speichert Verlauf und Fragen pro Verdächtigem: {suspect_id: {"history": [], "questions_asked": 0, "suspicion": 0}}
}

# --- API Endpunkte / Routen ---

@app.route('/scenarios', methods=['GET'])
def get_scenarios_endpoint():
    """ Liefert eine Liste der verfügbaren Szenarien. """
    scenarios = get_available_scenarios()
    return jsonify(scenarios)

@app.route('/start_scenario/<string:scenario_id>', methods=['POST'])
def start_scenario_endpoint(scenario_id):
    """ Lädt das ausgewählte Szenario und setzt den Spielzustand zurück. """
    print(f"Versuche Szenario zu starten: {scenario_id}")
    loaded_scenario = load_scenario(scenario_id)
    if loaded_scenario:
        game_state["current_scenario_id"] = loaded_scenario.id
        game_state["current_scenario"] = loaded_scenario
        game_state["interview_states"] = {} # Alten Verlauf löschen
        print(f"Szenario '{loaded_scenario.title}' erfolgreich gestartet.")
        # Gebe die Daten des gestarteten Szenarios zurück, damit das Frontend die Verdächtigenliste etc. hat
        suspects_summary = loaded_scenario.list_suspects_for_display()
        return jsonify({
            "message": "Szenario gestartet.",
            "scenario": {
                 "id": loaded_scenario.id,
                 "title": loaded_scenario.title,
                 "description": loaded_scenario.description,
                 "suspects": suspects_summary
            }
        })
    else:
        print(f"Fehler beim Starten von Szenario: {scenario_id}")
        return jsonify({"error": f"Szenario {scenario_id} konnte nicht geladen werden."}), 404


@app.route('/suspect/<string:suspect_id>/info', methods=['GET'])
def get_suspect_info_endpoint(suspect_id):
    """ Liefert detaillierte Infos zu einem spezifischen Verdächtigen des aktuellen Szenarios. """
    if not game_state["current_scenario"]:
        return jsonify({"error": "Kein Szenario aktiv. Bitte zuerst /start_scenario/<id> aufrufen."}), 400
        
    suspect = game_state["current_scenario"].get_suspect(suspect_id)
    if not suspect:
        return jsonify({"error": f"Verdächtiger mit ID {suspect_id} im aktuellen Szenario nicht gefunden."}), 404

    # Initialisiere den Interview-Status für diesen Verdächtigen, falls noch nicht geschehen
    if suspect_id not in game_state["interview_states"]:
         game_state["interview_states"][suspect_id] = {"history": [], "questions_asked": 0, "suspicion": 0, "suspicion_feedback_given": False}

    interview_state = game_state["interview_states"][suspect_id]
    questions_remaining = MAX_QUESTIONS_PER_SUSPECT - interview_state["questions_asked"]

    # Finde den passenden Hinweis (Logik wie zuvor)
    clue_map = { "activity_yesterday": "...", "job_satisfaction": "...", "hobby_skill": "...", "relationship_status": "...", "fake_trip": "..." } # Details aus scenario_data
    clue_map["job_satisfaction"] = "Es gibt Gerüchte, dass die Person mit ihrer aktuellen Arbeitssituation nicht ganz glücklich sein könnte."
    clue_map["hobby_skill"]= "Du fragst dich, ob die Person ihr angegebenes Hobby wirklich so intensiv betreibt..."
    clue_map["relationship_status"]= "Etwas an der Art, wie die Person über ihr Privatleben spricht, kommt dir seltsam vor."
    clue_map["fake_trip"]= "Die Erzählungen der Person über eine kürzliche Reise klangen fast zu perfekt."
    clue_map["activity_yesterday"]= "Du hast gehört, dass die Person gestern Abend vielleicht doch nicht so einen ruhigen Abend hatte..."


    starting_clue = clue_map.get(suspect.secret_type, "")

    suspect_info = {
        "id": suspect.id, "name": suspect.name, "background": suspect.background,
        "alibi": suspect.alibi, "questions_remaining": questions_remaining,
        "starting_clue": starting_clue
    }
    return jsonify(suspect_info)


@app.route('/ask', methods=['POST'])
def ask_suspect_endpoint():
    """ Nimmt eine Frage entgegen, ermittelt die Antwort (Hybrid) und gibt sie inkl. Stresslevel zurück. """
    data = request.get_json()
    if not data or 'question' not in data or 'suspect_id' not in data:
        return jsonify({"error": "Fehlende Daten: 'question' und 'suspect_id' benötigt."}), 400

    question = data['question']
    suspect_id = data['suspect_id'].upper() # Stelle sicher, dass ID groß ist
    
    if not game_state["current_scenario"]:
        return jsonify({"error": "Kein Szenario aktiv."}), 400
    
    suspect = game_state["current_scenario"].get_suspect(suspect_id)
    if not suspect:
        return jsonify({"error": f"Verdächtiger {suspect_id} nicht gefunden."}), 404
        
    # Hole Zustand für diesen Verdächtigen oder initialisiere
    if suspect_id not in game_state["interview_states"]:
         game_state["interview_states"][suspect_id] = {"history": [], "questions_asked": 0, "suspicion": 0, "suspicion_feedback_given": False}
    interview_state = game_state["interview_states"][suspect_id]

    # Prüfe Fragenlimit
    if interview_state["questions_asked"] >= MAX_QUESTIONS_PER_SUSPECT:
         return jsonify({"error": "Maximalzahl Fragen für diesen Verdächtigen erreicht.", "answer": "(Keine Fragen mehr übrig)", "questions_remaining": 0}), 400

    interview_state["questions_asked"] += 1
    
    # Hybrid-Antwort holen (get_answer muss hier verfügbar sein oder importiert werden)
    # Wir definieren get_answer hier temporär, besser wäre Import aus main.py oder eigener Logik-Datei
    def get_hybrid_answer(suspect_obj, question_text, history):
         normalized_q = question_text.lower().strip()
         # Einfache Fakten-Checks (Beispiele)
         if "name" in normalized_q: return f"Mein Name ist {suspect_obj.name}."
         if "alter" in normalized_q: return f"Ich bin {suspect_obj.age} Jahre alt."
         if "job" in normalized_q: return f"Ich arbeite als {suspect_obj.job}."
         alibi_kw = ["alibi", "tatzeit", "gestern", "wo waren sie", "19 uhr", "20 uhr", "21 uhr", "gemacht"]
         if any(kw in normalized_q for kw in alibi_kw): return f"Zu dieser Zeit? {suspect_obj.alibi}"
         if "anwesenheit" in normalized_q and "büro" in normalized_q:
              fact = suspect_obj.known_facts.get("anwesenheit_büro_tatzeit")
              if fact is not None: return str(fact)
         # Fallback: LLM
         print("[INFO] Frage erfordert LLM...", flush=True)
         return get_perplexity_response(suspect_obj, question_text, history)

    # Antwort ermitteln
    answer = get_hybrid_answer(suspect, question, interview_state["history"])

    # Stress / Suspicion berechnen (basierend auf aktueller Frage)
    shows_stress = False
    for keyword in suspect.keywords:
        if keyword in question.lower():
            shows_stress = True
            interview_state["suspicion"] += 1
            break
            
    stress_indicator_msg = None
    getting_closer_hint = None
    if shows_stress:
        stress_reactions = ["[INFO] Die Person räuspert sich kurz...", "[INFO] Die Person blickt kurz zur Seite...", "[INFO] Die Person scheint zu zögern...", "[INFO] Ein Zucken im Mundwinkel?"]
        stress_indicator_msg = random.choice(stress_reactions)
        
    if interview_state["suspicion"] >= SUSPICION_THRESHOLD and not interview_state["suspicion_feedback_given"]:
         getting_closer_hint = f"[INFO] Deine Fragen zu diesem Thema scheinen {suspect.name} unter Druck zu setzen..."
         interview_state["suspicion_feedback_given"] = True # Nur einmal anzeigen

    # *** NEU: Herzschlag berechnen ***
    base_heartbeat = 75
    stress_increase = interview_state["suspicion"] * 8 # Z.B. 8 Schläge pro Verdachtspunkt
    random_fluctuation = random.randint(-4, 4)
    current_heartbeat = min(base_heartbeat + stress_increase + random_fluctuation, 135) # Obergrenze

    # Stress-Level bestimmen
    stress_level = "Ruhe"
    if 85 <= current_heartbeat < 105:
        stress_level = "Angespannt"
    elif current_heartbeat >= 105:
        stress_level = "Stress!"
        
    # Gesprächsverlauf aktualisieren
    interview_state["history"].append({"role": "user", "content": question})
    if answer and not answer.startswith("[Fehler"):
        interview_state["history"].append({"role": "assistant", "content": answer})
    else:
        interview_state["history"].append({"role": "assistant", "content": "(Antwort Fehler)"})

    # Antwort für Frontend zusammenstellen
    response_data = {
        "answer": answer,
        "stress_indicator": stress_indicator_msg, # Die nervöse Reaktion
        "getting_closer_hint": getting_closer_hint,
        "questions_remaining": MAX_QUESTIONS_PER_SUSPECT - interview_state["questions_asked"],
        # NEU: Herzschlag-Daten hinzufügen
        "heartbeat_bpm": current_heartbeat,
        "stress_level_text": stress_level 
    }
    return jsonify(response_data)


@app.route('/accuse', methods=['POST'])
def accuse_suspect_endpoint():
    """ Nimmt eine Beschuldigung entgegen und gibt das Ergebnis zurück. """
    data = request.get_json()
    if not data or 'suspect_id' not in data:
         return jsonify({"error": "Fehlende Daten: 'suspect_id' benötigt."}), 400
         
    if not game_state["current_scenario"]:
        return jsonify({"error": "Kein Szenario aktiv."}), 400
        
    accused_id = data['suspect_id'].upper()
    accused_suspect = game_state["current_scenario"].get_suspect(accused_id)
    actual_culprit_id = game_state["current_scenario"].culprit_id

    response_data = {}
    if accused_suspect and accused_suspect.id == actual_culprit_id:
         culprit = accused_suspect # Alias für Klarheit
         response_data["correct"] = True
         response_data["message"] = f"Korrekt! {culprit.name} war der Täter.\nDas Motiv/Geheimnis war: {culprit.secret_details}\nFall abgeschlossen! Du hast gewonnen!"
    elif accused_suspect:
         culprit = game_state["current_scenario"].get_suspect(actual_culprit_id)
         response_data["correct"] = False
         response_data["message"] = f"Falsch! {accused_suspect.name} war unschuldig.\nDer wahre Täter war {culprit.name}.\nDessen Motiv/Geheimnis war: {culprit.secret_details}\nDu hast verloren."
    else:
         response_data["correct"] = False
         response_data["message"] = "Ungültige Auswahl für die Beschuldigung. Du hast verloren."
         
    # Optional: Spielzustand zurücksetzen nach Auflösung
    # game_state["current_scenario_id"] = None 
    # game_state["current_scenario"] = None
    # game_state["interview_states"] = {}

    return jsonify(response_data)


# --- App starten ---
if __name__ == '__main__':
    check_config() 
    print("Starte Flask Backend Server auf http://localhost:5000 ...")
    app.run(host='0.0.0.0', port=8004, debug=True) # host='0.0.0.0' kann wichtig sein

