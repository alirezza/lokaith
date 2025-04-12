# llm_interaction.py
import requests
import json
from config import (
    PERPLEXITY_API_KEY, PERPLEXITY_API_URL, PERPLEXITY_MODEL, LLM_TIMEOUT
)

def get_perplexity_response(suspect, user_question, conversation_history):
    """ 
    Sendet die Frage an die Perplexity API und erhält eine Antwort im Charakter des Verdächtigen.
    Nimmt jetzt das 'suspect' Objekt für detailliertere Prompts.
    """
    if not PERPLEXITY_API_KEY: 
        print("Warnung: Perplexity API Key fehlt.")
        return "[Fehler: API Key fehlt]" 

    # --- Prompt Engineering ---
    system_prompt = f"""Du bist eine KI, die die fiktive Person '{suspect.name}' spielt. Antworte auf Fragen eines Detektivs auf Deutsch. Bleibe im Charakter basierend auf diesem Profil:
- Name: {suspect.name}
- Alter: {suspect.age}
- Job: {suspect.job}
- Hintergrund: {suspect.background}
- Dein Alibi für gestern Abend (19-21 Uhr): {suspect.alibi}
"""
    secret_type = suspect.secret_type
    secret_details = suspect.secret_details

    if secret_type and secret_details:
        # Spezifische Anweisung für den Täter vs. andere Verdächtige
        if suspect.is_culprit:
             system_prompt += f"\nWICHTIGES GEHEIMNIS (DU BIST DER TÄTER!):\n- DEIN GEHEIMNIS ({secret_type}): {secret_details}\n"
             system_prompt += "- ANWEISUNG: Du bist der Täter! Leugne deine Tat vehement. Wenn der Detektiv Fragen stellt, die dein Geheimnis oder deine Schuld berühren könnten, musst du überzeugend lügen, ausweichen oder das Thema wechseln. Gib das Geheimnis oder deine Schuld unter keinen Umständen zu! Antworte ansonsten konsistent mit deinem Profil und Alibi.\n"
        else:
             system_prompt += f"\nWICHTIGES GEHEIMNIS (Du bist unschuldig, hast aber dies zu verbergen):\n- DEIN GEHEIMNIS ({secret_type}): {secret_details}\n"
             system_prompt += "- ANWEISUNG: Du bist unschuldig am Hauptvorwurf, hast aber dieses kleinere Geheimnis. Wenn Fragen dein Geheimnis berühren, versuche auszuweichen oder es herunterzuspielen, aber lüge nicht über das Hauptverbrechen (z.B. den Datendiebstahl). Gib dein kleines Geheimnis nur zu, wenn du direkt darauf angesprochen wirst und es nicht mehr leugnen kannst. Antworte ansonsten konsistent mit deinem Profil und Alibi.\n"
    else:
        system_prompt += "\n- Du hast kein besonderes Geheimnis zu verbergen. Antworte ehrlich und konsistent basierend auf deinem Profil und Alibi.\n"

    system_prompt += "\nAntworte immer kurz und natürlich auf Deutsch."

    messages = [{"role": "system", "content": system_prompt}]
    for entry in conversation_history:
         role = entry.get('role'); content = entry.get('content')
         if role == 'model': role = 'assistant' 
         if role in ['user', 'assistant'] and content: messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_question})
    
    headers = {"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json", "Accept": "application/json"}
    payload = { "model": PERPLEXITY_MODEL, "messages": messages }

    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=LLM_TIMEOUT) 
        response.raise_for_status(); api_response_data = response.json()
        if api_response_data and 'choices' in api_response_data and len(api_response_data['choices']) > 0:
            assistant_message = api_response_data['choices'][0].get('message', {}).get('content')
            if assistant_message: return assistant_message.strip()
            else: print("   [LLM Call] Perplexity ERROR: Keine Antwort im erwarteten Format.")
        else: print("   [LLM Call] Perplexity ERROR: Unerwartetes Antwortformat.")
        return "[Fehler: Konnte keine gültige Antwort von Perplexity extrahieren]"
    except requests.exceptions.Timeout: print(f"   [LLM Call] Perplexity ERROR: Timeout nach {LLM_TIMEOUT}s."); return "[Fehler: Zeitüberschreitung]"
    except requests.exceptions.RequestException as e:
        error_text = f" Status Code: {e.response.status_code}, Response: {e.response.text}" if e.response is not None else ""
        print(f"   [LLM Call] Perplexity ERROR: {e}{error_text}"); return f"[Fehler: {e}]"
    except json.JSONDecodeError: print("   [LLM Call] Perplexity ERROR: JSON Decode Error."); return "[Fehler: JSON Decode]"

