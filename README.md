# 🕵️‍♂️ Lokaith – Das KI-Detektivspiel

**Lokaith** ist ein interaktives Detektivspiel mit Spracherkennung (STT), Sprachausgabe (TTS) und generativer KI. Du befragst eine zufällig generierte Person – sie hat möglicherweise ein Geheimnis. Finde mit gezielten Fragen heraus, ob sie lügt.

---

## 🔍 Features

- 🎭 Dynamische Charaktere durch echte API-Daten
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
```

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

## 📦 Anforderungen

- Python 3.9 oder neuer
- Internetverbindung für API-Zugriffe
- Mikrofon (für Spracheingabe)
- Lautsprecher (für Sprachausgabe)

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
