# scenario_data.py
import random

# --- Datenstrukturen ---
class Suspect:
    """Repräsentiert eine verdächtige Person im Spiel (mit mehr Details)."""

    def __init__(
        self,
        id,
        name,
        age,
        job,
        appearance,
        personality,
        background,
        alibi,
        is_culprit=False,
        secret_type=None,
        secret_details=None,
        keywords=None,
        known_facts=None,
        bonus_clues=None,
    ):
        self.id = id 
        self.name = name; self.age = age; self.job = job
        # NEU: Detailliertere Beschreibung
        self.appearance = appearance # Kurze Beschreibung des Aussehens
        self.personality = personality # Liste von Stichworten zum Verhalten/Charakter
        self.background = background # Längere Hintergrundgeschichte
        self.alibi = alibi # Spezifisches Alibi für die Tatzeit
        self.is_culprit = is_culprit 
        self.secret_type = secret_type 
        self.secret_details = secret_details 
        self.keywords = keywords if keywords else []
        self.bonus_clues = bonus_clues or []
        # Erweitertes known_facts für direkte Antworten
        self.known_facts = known_facts if known_facts else {} 
        # Füge Standard-Fakten hinzu, die aus anderen Feldern abgeleitet werden
        self.known_facts.setdefault("name", self.name)
        self.known_facts.setdefault("alter", str(self.age))
        self.known_facts.setdefault("job", self.job)
        self.known_facts.setdefault("alibi", self.alibi)
        self.known_facts.setdefault("aussehen", self.appearance)


    def get_bonus_hint(self):
        """Gibt einen zufälligen Hinweis dieses Verdächtigen zurück."""
        if not self.bonus_clues:
            return None
        return random.choice(self.bonus_clues)


    def get_profile_summary(self):
        """ Gibt eine kurze Zusammenfassung für die Auswahl. """
        return f"{self.name} ({self.age}), {self.job}"

    def get_initial_info(self):
        """ Gibt die erweiterten Informationen zurück, die der Spieler vor der Befragung sieht. """
        info = f"Name: {self.name}\n"
        info += f"Alter: {self.age}\n"
        info += f"Job: {self.job}\n"
        info += f"Aussehen: {self.appearance}\n"
        info += f"Persönlichkeit: {', '.join(self.personality)}\n"
        info += f"Hintergrund: {self.background}\n"
        info += f"Alibi (für gestern 19-21 Uhr): {self.alibi}"
        return info

class Scenario:
    """ Repräsentiert ein Ermittlungs-Szenario (mit mehr Details). """
    def __init__(self, id, title, description, scene_details, suspects, bonus_clues=None):
        self.id = id
        self.title = title
        self.description = description  # Hauptbeschreibung des Falls
        # NEU: Details zum Schauplatz
        self.scene_details = scene_details
        self.suspects = {s.id.upper(): s for s in suspects}
        self.culprit_id = next((s.id for s in suspects if s.is_culprit), None)
        if not self.culprit_id:
            print(f"WARNUNG: Szenario '{title}' hat keinen Täter!")
        self.bonus_clues = bonus_clues or []

    def get_bonus_hint(self, suspect_id=None):
        """Gibt einen zufälligen Bonus-Hinweis zurück."""
        if suspect_id:
            suspect = self.get_suspect(suspect_id)
            if suspect:
                hint = suspect.get_bonus_hint()
                if hint:
                    return hint
        if not self.bonus_clues:
            return None
        return random.choice(self.bonus_clues)
             
    def list_suspects_for_display(self):
         """ Gibt eine Liste von Dicts für die Frontend-Anzeige zurück. """
         return [{"id": s.id, "name": s.name, "job": s.job} for s in self.suspects.values()]

    def list_suspects(self):
        """Gibt die verfügbaren Verdächtigen mit ihren IDs auf der Konsole aus."""
        print("\n-- Verf\xC3\xBCgbare Verd\xC3\xA4chtige --")
        for s in self.suspects.values():
            print(f"[{s.id}] {s.get_profile_summary()}")

    def get_suspect(self, s_id):
        """ Gibt das Objekt des Verdächtigen anhand der ID zurück (Großbuchstaben). """
        return self.suspects.get(s_id.upper())

# --- Liste aller verfügbaren Szenario-Definitionen (unverändert) ---
available_scenarios_list = [
    {"id": "SPIONAGE01", "title": "Datendiebstahl bei TechCorp", "description": "Bei TechCorp wurden sensible Kundendaten und Marketingpläne gestohlen..."},
    {"id": "MORD01", "title": "Mord in der Villa Edelstein", "description": "Der reiche Philanthrop Baron von Edelstein wurde tot aufgefunden..."},
    {"id": "DIEBSTAHL01", "title": "Der gestohlene Saphir", "description": "Während einer Gala wurde der berühmte 'Stern des Ozeans'-Saphir gestohlen..."}
]

def get_available_scenarios():
    """ Gibt eine Liste der verfügbaren Szenarien zurück. """
    return available_scenarios_list

# --- Funktion zum Laden eines spezifischen Szenarios ---
def load_scenario(scenario_id):
    """ Lädt und gibt ein spezifisches Szenario-Objekt zurück (mit angereicherten Daten). """
    
    # === Szenario 1: Firmenspionage (Angereichert) ===
    if scenario_id.upper() == "SPIONAGE01":
        suspect1 = Suspect(
            id="A", name="Peter Schmidt", age=45, job="Leitender Entwickler",
            appearance="Trägt eine etwas altmodische Brille, wirkt gestresst, leicht graue Schläfen.",
            personality=["Loyal", "Verschlossen", "Gestresst", "Korrekt"],
            background="Ist seit über 15 Jahren bei TechCorp und kennt die Kernsysteme wie seine Westentasche. Gilt als absolut zuverlässig, aber Kollegen beschreiben ihn als distanziert. Lebt allein. Gerüchte über kürzliche finanzielle Engpässe machen die Runde.",
            alibi="War zur Tatzeit (gestern, 19-21 Uhr) nachweislich im Büro im 3. Stock und hat am 'Projekt Phoenix' gearbeitet. Ein Kollege hat ihn gegen 19:30 Uhr kurz gesehen, danach war er allein.",
            is_culprit=False, secret_type="private_debt",
            secret_details="Du hast hohe private Spielschulden bei zwielichtigen Gestalten, die Druck machen. Du brauchst dringend Geld, aber du würdest niemals deine Firma bestehlen. Du hast Angst, dass die Schulden rauskommen.",
            keywords=["geld", "finanzen", "schulden", "überstunden", "allein", "büro", "privat", "probleme", "projekt phoenix", "druck"],
            known_facts={ # Erweiterte Fakten für direkte Antworten
                "anwesenheit_büro_tatzeit": "Ja, ich habe gestern Abend bis spät am Projekt Phoenix gearbeitet.", 
                "job_bezeichnung": "Leitender Entwickler bei TechCorp.",
                "firma": "TechCorp",
                "projekt": "Projekt Phoenix, eine wichtige neue Software-Komponente.",
                "finanzielle_situation": "Äh... darüber möchte ich nicht sprechen. Es ist alles in Ordnung.", # Beispiel für ausweichende, aber feste Antwort
                "kollegen_gesehen": "Ja, Herr Müller aus dem Nachbarbüro war bis etwa halb acht noch da."
                },
            bonus_clues=[
                "Auf seinem Schreibtisch liegen viele unbezahlte Rechnungen.",
                "Ein Kollege hörte ihn kürzlich über Geldprobleme reden."
            ]
        )
        suspect2 = Suspect(
            id="B", name="Sandra Meier", age=35, job="Marketing Managerin",
            appearance="Trägt moderne Geschäftskleidung, wirkt sehr selbstbewusst und dynamisch.",
            personality=["Ehrgeizig", "Selbstbewusst", "Eloquent", "Ungeduldig"],
            background="Kam erst vor 8 Monaten zu TechCorp und hat schnell Karriere gemacht. Ist bekannt für ihren Ehrgeiz und ihre manchmal rücksichtslosen Methoden. Hat weitreichenden Zugang zu Marketingdaten und Kundenlisten.",
            alibi="War zur Tatzeit (gestern, 19-21 Uhr) angeblich auf einem Geschäftsessen im teuren Restaurant 'La Lune' mit einem wichtigen Neukunden. Den Namen des Kunden will sie (noch) nicht nennen.",
            is_culprit=True, secret_type="corporate_espionage",
            secret_details="Du verkaufst seit Monaten regelmäßig Kundendaten und Marketingstrategien an einen Konkurrenten (Apex Solutions), um deine Karriere voranzutreiben und dir einen luxuriösen Lebensstil zu finanzieren. Das Geschäftsessen war nur ein Vorwand; du hast dich kurz mit deinem Kontakt von Apex getroffen, um die neuesten Daten zu übergeben.",
            keywords=["marketing", "kunden", "daten", "strategie", "konkurrenz", "apex", "geschäftsessen", "karriere", "geld", "vertraulich", "neue", "ehrgeizig", "restaurant", "la lune"],
             known_facts={
                 "anwesenheit_büro_tatzeit": "Nein, ich war bei einem wichtigen Geschäftsessen im 'La Lune'.",
                 "job_bezeichnung": "Marketing Managerin bei TechCorp.",
                 "firma": "TechCorp",
                 "kunde_name": "Das ist im Moment noch vertraulich, es geht um einen großen potenziellen Deal.", # Ausweichende Antwort
                 "restaurant": "Im 'La Lune', ein sehr gutes Restaurant."
                 },
            bonus_clues=[
                "Im Papierkorb liegt eine Visitenkarte von 'Apex Solutions'.",
                "Sie wurde kürzlich beim Kauf teurer Geschenke gesehen."
            ]
        )
        suspect3 = Suspect(
            id="C", name="Klaus Huber", age=58, job="Hausmeister",
            appearance="Freundliches Gesicht, trägt Arbeitskleidung, wirkt etwas müde.",
            personality=["Freundlich", "Neugierig", "Langjährig", "Verlässlich"],
            background="Der gute Geist der Firma, arbeitet seit über 25 Jahren hier. Kennt alle und jeden Winkel des Gebäudes. Ist bekannt dafür, gerne mal einen Plausch zu halten und manchmal etwas zu neugierig zu sein.",
            alibi="Hat seine übliche späte Reinigungsrunde im gesamten Gebäude gemacht (gestern, ca. 18:30-21:30 Uhr). Er war in vielen Büros, auch im Marketing und der Entwicklung, kann aber keine genauen Zeitfenster für einzelne Räume nennen.",
            is_culprit=False, secret_type="minor_theft",
            secret_details="Du nimmst öfter mal Büromaterial (Stifte, Blöcke) und vor allem den guten Kaffee aus der Chefetage für zuhause mit. Es ist nicht viel, aber du hast Angst, dass es mal auffällt und du Ärger bekommst.",
            keywords=["reinigung", "gebäude", "unterwegs", "gesehen", "allein", "material", "kaffee", "mitgenommen", "hausmeister", "zugang", "runde", "schlüssel"],
            known_facts={
                "anwesenheit_büro_tatzeit": "Nein, nicht fest in einem Büro, ich habe meine Runde gemacht.",
                "job_bezeichnung": "Ich bin hier der Hausmeister.",
                "firma": "TechCorp",
                "runde_details": "Ich war überall mal, im 3. Stock bei der Entwicklung, im 2. beim Marketing... wie jeden Abend.",
                "etwas_gesehen": "Nein, eigentlich war alles ruhig. Nur Herr Schmidt war noch da oben."
                },
            bonus_clues=[
                "Er besitzt einen Generalschlüssel für fast alle Räume.",
                "Er erinnert sich an jedes Geräusch im Gebäude."
            ]
        )
        
        scenario_info = next((s for s in available_scenarios_list if s["id"] == "SPIONAGE01"), None)
        bonus_clues = [
            "Auf einem Notizzettel steht der Name 'Apex' geschrieben.",
            "Jemand hat kurz nach 20 Uhr hektisch das Gebäude verlassen.",
            "Im Marketingbüro riecht es nach teurem Parfüm.",
        ]
        return Scenario(
            id="SPIONAGE01",
            title=scenario_info['title'],
            description=scenario_info['description'],
            scene_details="Die Büros von TechCorp sind modern, aber gestern Abend wirkten die Flure verlassen. Im Marketingbereich wurde eine offen gelassene Schublade gefunden.",
            suspects=[suspect1, suspect2, suspect3],
            bonus_clues=bonus_clues,
        )
        
    # === Szenario 2: Mordfall (Müsste ebenso angereichert werden) ===
    elif scenario_id.upper() == "MORD01":
        # ... (Definitionen für Butler, Nichte, Partner hier anreichern) ...
        print("WARNUNG: Szenario MORD01 ist noch nicht vollständig angereichert.")
        # Gib vorerst das alte zurück oder None
        return None # Beispiel: Szenario noch nicht spielbar

    # === Szenario 3: Artefaktdiebstahl (Müsste ebenso angereichert werden) ===
    elif scenario_id.upper() == "DIEBSTAHL01":
         # ... (Definitionen für Kritikerin, Wache, Dieb hier anreichern) ...
        print("WARNUNG: Szenario DIEBSTAHL01 ist noch nicht vollständig angereichert.")
        return None # Beispiel: Szenario noch nicht spielbar
        
    else:
        print(f"FEHLER: Szenario mit ID '{scenario_id}' nicht gefunden.")
        return None

