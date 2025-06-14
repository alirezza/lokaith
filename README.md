# 🕵️‍♂️ Lokaith – Das KI-Detektivspiel

**Lokaith** ist ein interaktives Detektivspiel mit Spracherkennung (STT), Sprachausgabe (TTS) und generativer KI. Du befragst eine zufällig generierte Person – sie hat möglicherweise ein Geheimnis. Finde mit gezielten Fragen heraus, ob sie lügt.

---

## 🔍 Features

- 🎭 API-Vorbereitung für dynamische Charaktere (noch nicht aktiv)
- 🤖 KI-gesteuerte Antworten via Perplexity AI (sonar)
- 🗣️ Sprachsteuerung: Frage per Mikrofon
- 🔊 TTS-Ausgabe mit Stimme (wenn verfügbar)
- 🧠 Zufällige Geheimnisse & Reaktionsmuster
- 📈 Steigende Spannung durch **Verdachts-Indikator**
- 🔐 Kleines Minispiel "Codebreaker" zum Freischalten zusätzlicher Hinweise
- 🕵️‍♀️ Minispiel "Spurenanalyse" zum Zuordnen von Hinweisen
- 🎴 Gedächtnisspiel "Aussagen merken" für bessere Beobachtung
- 💬 Minispiel "Lügendetektor" zum Aufdecken von Stressmustern
- 🧩 Minispiel "Indizien-Puzzle" zum Zusammensetzen von Fotos
- 📂 Minispiel "Beweismittelkette" zum zeitlichen Zuordnen von Beweisen
- Neu: Während der Befragung kannst du mit dem Befehl `minigame` ein zufälliges
  Minispiel starten, um einen zusätzlichen Hinweis zu erhalten.

---

## 🗺️ Szenarien-Status

Derzeit ist nur das Szenario **SPIONAGE01** voll spielbar. Die übrigen Szenarien sind noch unvollständig und dienen als Platzhalter.

## ⚙️ Setup

### 1. Klone das Repository

```bash
git clone https://github.com/alirezza/lokaith.git
cd lokaith
```

### 2. Erstelle und aktiviere eine virtuelle Umgebung

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installiere die Abhängigkeiten

```bash
pip install -r requirements.txt
```

### 4. Lege eine `.env` Datei an mit deinem Perplexity API Key

```env
PERPLEXITY_API_KEY=dein_api_key
PERPLEXITY_MODEL=sonar-small-chat
```

> `config.py` erwartet die Umgebungsvariable `PERPLEXITY_MODEL`,
> die angibt, welches Perplexity-Modell genutzt wird (z.B.
> `sonar-small-chat`).

### Tests ausführen

Nach dem Einrichten der Umgebung kannst du die automatischen Tests mit

```bash
pytest
```

---

## ▶️ Spiel starten

```bash
python main.py
```

---

## ✨ Web-Frontend nutzen

Zusätzlich zum Konsolenspiel gibt es eine Flask-API (`app.py`) und ein kleines
Web-Frontend (`index.html`, `script.js`, `styles.css`). So startest du die Web-
Variante:

1. **Backend starten**

```bash
python app.py
```

   Der Server läuft standardmäßig auf <http://localhost:8004>.

2. **Frontend aufrufen**

   Öffne `index.html` direkt im Browser oder starte einen einfachen HTTP-Server
   und rufe die Seite dann auf:

```bash
python -m http.server
```

   Die Datei erreichst du anschließend unter
   <http://localhost:8000/index.html>. Achte darauf, dass in `script.js` die
   Konstante `BASE_URL` auf die Adresse deines Backends zeigt.

---

## 🐳 Docker nutzen

Neben der Ausführung auf dem Host kannst du das Projekt auch in Containern
starten. Es gibt zwei Varianten:

1. **Dev Docker** – bindet deinen Quellcode als Volume ein und eignet sich
   für schnelle lokale Anpassungen.

```bash
docker compose -f docker-compose.dev.yml up --build
```

2. **Prod Docker** – ohne Volume. Diese Variante wird z.B. in GitLab CI/CD
   verwendet.

```bash
docker compose -f docker-compose.prod.yml up --build
```

Beide Konfigurationen lesen deine `.env` Datei und stellen das Backend unter
<http://localhost:8004> bereit.

---

## 🤖 GitHub Actions

Bei jedem Push laufen die Tests automatisch. Die Konfiguration findest du in
`.github/workflows/ci.yml`.

---

## 📦 Anforderungen

- Python 3.8 bis 3.11\*
- Internetverbindung für API-Zugriffe
- Mikrofon (für Spracheingabe)
- Lautsprecher (für Sprachausgabe)

\* Das Python-Paket `openai-whisper` unterstützt derzeit keine Python-Versionen
ab 3.12. Verwende daher eine Umgebung mit Python 3.11 oder älter, damit die
Installation mit `pip install -r requirements.txt` funktioniert.

---

## 📌 Hinweise

- Das Spiel verwendet Daten von:
  - [randomuser.me](https://randomuser.me/)
  - [dummyjson.com](https://dummyjson.com/users)
  - [agify.io](https://agify.io/)
- Antworten werden live von **Perplexity AI** generiert.
- Das Whisper-Modell wird lokal verwendet für Spracherkennung.

---

## 🧪 Beispiel-Fragen

- *Was hast du gestern Abend gemacht?*
- *Gefällt dir deine Arbeit wirklich?*
- *Warst du am Wochenende verreist?*

---

## 🛡️ Sicherheit

Dein API-Key wird **nicht im Code gespeichert** – er wird über eine Umgebungsvariable (`.env`) geladen. Die `.env`-Datei steht in der `.gitignore` und wird **nicht gepusht**.

---

## 🧠 Inspiration

**Lokaith** ist inspiriert von Ideen aus interaktiven Erzählspielen, KI-Dialogsystemen und mythologischer Täuschungskunst.

---

## 📝 Lizenz

MIT License – frei zur Nutzung und Weiterentwicklung.

---
