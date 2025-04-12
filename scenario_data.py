# scenario_data.py
import random

# --- Datenstrukturen ---
class Suspect:
    """ Repräsentiert eine verdächtige Person im Spiel. """
    def __init__(self, id, name, age, job, background, alibi, is_culprit=False, secret_type=None, secret_details=None, keywords=None, known_facts=None):
        self.id = id 
        self.name = name
        self.age = age
        self.job = job
        self.background = background 
        self.alibi = alibi 
        self.is_culprit = is_culprit 
        self.secret_type = secret_type 
        self.secret_details = secret_details 
        self.keywords = keywords if keywords else [] 
        self.known_facts = known_facts if known_facts else {} # Fakten für direkte Antworten

    def get_profile_summary(self):
        """ Gibt eine kurze Zusammenfassung für die Auswahl. """
        return f"{self.name} ({self.age}), {self.job}"

    def get_initial_info(self):
        """ Gibt die Informationen zurück, die der Spieler vor der Befragung sieht. """
        return f"Name: {self.name}\nAlter: {self.age}\nJob: {self.job}\nHintergrund: {self.background}\nAlibi: {self.alibi}"

class Scenario:
    """ Repräsentiert ein Ermittlungs-Szenario. """
    def __init__(self, id, title, description, suspects):
        self.id = id
        self.title = title
        self.description = description 
        self.suspects = {s.id: s for s in suspects} 
        self.culprit_id = next((s.id for s in suspects if s.is_culprit), None) # Finde Täter-ID
        if not self.culprit_id:
             print(f"WARNUNG: Szenario '{title}' hat keinen definierten Täter!")
             
    def list_suspects(self):
        """ Gibt eine Liste der Verdächtigen zur Auswahl aus. """
        print("\nVerdächtige Personen:")
        for s_id, suspect in self.suspects.items():
            print(f"  [{s_id}] {suspect.get_profile_summary()}")
            
    def get_suspect(self, s_id):
        """ Gibt das Objekt des Verdächtigen anhand der ID zurück. """
        # Mache die Auswahl case-insensitive
        return self.suspects.get(s_id.upper())


# --- Szenario Definitionen ---

def load_scenario(scenario_id="SPIONAGE01"):
    """ Lädt und gibt ein spezifisches Szenario zurück. """
    
    # --- Beispiel-Szenario: Firmenspionage ---
    if scenario_id == "SPIONAGE01":
        suspect1 = Suspect(
            id="A", name="Peter Schmidt", age=45, job="Leitender Entwickler",
            background="Langjähriger Mitarbeiter, gilt als loyal, aber etwas verschlossen. Hatte kürzlich finanzielle Engpässe.",
            alibi="War zur Tatzeit (gestern, 19-21 Uhr) angeblich allein im Büro und hat Überstunden gemacht.",
            is_culprit=False, secret_type="private_debt",
            secret_details="Du hast hohe private Spielschulden, von denen niemand in der Firma weiß. Du hast Angst, dass es rauskommt und du deinen Job verlierst.",
            keywords=["geld", "finanzen", "schulden", "überstunden", "allein", "büro", "privat", "probleme"],
            known_facts={"anwesenheit_büro_tatzeit": "Ja, ich habe gestern Abend lange gearbeitet.", 
                         "job_bezeichnung": "Leitender Entwickler"}
        )
        suspect2 = Suspect(
            id="B", name="Sandra Meier", age=35, job="Marketing Managerin",
            background="Relativ neu in der Firma, sehr ehrgeizig. Hat Zugang zu vielen sensiblen Marketing- und Kundendaten.",
            alibi="War zur Tatzeit (gestern, 19-21 Uhr) angeblich auf einem späten Geschäftsessen mit einem (nicht näher genannten) Kunden.",
            is_culprit=True, secret_type="corporate_espionage",
            secret_details="Du verkaufst seit Monaten regelmäßig Kundendaten und Marketingstrategien an einen Konkurrenten, um deine Karriere voranzutreiben und schnelles Geld zu machen. Das Geschäftsessen war nur ein Vorwand, um Daten zu übergeben.",
            keywords=["marketing", "kunden", "daten", "strategie", "konkurrenz", "geschäftsessen", "karriere", "geld", "vertraulich", "neue", "ehrgeizig"],
             known_facts={"anwesenheit_büro_tatzeit": "Nein, ich war bei einem Geschäftsessen.",
                          "job_bezeichnung": "Marketing Managerin"}
        )
        suspect3 = Suspect(
            id="C", name="Klaus Huber", age=58, job="Hausmeister",
            background="Arbeitet schon ewig hier, kennt jeden Winkel. Ist manchmal etwas neugierig und war zur Tatzeit im Gebäude unterwegs.",
            alibi="Hat seine übliche späte Reinigungsrunde gemacht (gestern, 19-21 Uhr), kann aber nicht genau sagen, wo er Minute für Minute war.",
            is_culprit=False, secret_type="minor_theft",
            secret_details="Du nimmst manchmal Büromaterial oder Kaffee für den privaten Gebrauch mit nach Hause. Nichts Großes, aber du willst nicht, dass es auffliegt.",
            keywords=["reinigung", "gebäude", "unterwegs", "gesehen", "allein", "material", "kaffee", "mitgenommen", "hausmeister", "zugang"],
            known_facts={"anwesenheit_büro_tatzeit": "Nein, nicht im Büro, aber im Gebäude unterwegs.",
                         "job_bezeichnung": "Hausmeister"}
        )
        
        return Scenario(
            id="SPIONAGE01", title="Datendiebstahl bei TechCorp",
            description="Bei der Firma TechCorp wurden sensible Kundendaten und Marketingpläne gestohlen und vermutlich an die Konkurrenz verkauft. Der Diebstahl muss gestern Abend zwischen 19 und 21 Uhr stattgefunden haben. Du sollst herausfinden, welcher der drei Hauptverdächtigen dahintersteckt.",
            suspects=[suspect1, suspect2, suspect3]
        )
        
    # Hier könnten weitere Szenarien mit anderen IDs hinzugefügt werden
    # elif scenario_id == "MORD01": ...
        
    else:
        print(f"FEHLER: Szenario mit ID '{scenario_id}' nicht gefunden.")
        return None

