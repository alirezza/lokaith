
// Globale Variablen und Zustand
let currentScenarioId = null; // NEU: ID des aktiven Szenarios
let currentSuspectId = null;
let scenarioData = null; // Speichert alle Szenarien ODER das aktuell geladene
let speechEnabled = false;
let recognition = null; 
let ttsUtterance = null; 
const MAX_QUESTIONS_PER_SUSPECT = 10; // TODO: Aus config holen oder vom Backend?

// DOM Elemente Caching
let loadingIndicator, errorDisplay, scenarioTitle, scenarioDescription, 
    scenarioSelectionView, // NEU
    scenarioList, // NEU
    startView, suspectList, interrogationView, suspectName, suspectInfo, dialogue, 
    questionInput, questionsRemainingElement, accusationView, accusationList, 
    resultView, resultHeading, resultMessage, ttsToggleButton, sendButton, 
    speechButton, changeSuspectButton, accuseButton, accuseConfirmButton, 
    cancelAccusationButton, newGameButton,
    stressIndicatorDisplay, // NEU
    heartbeatDisplay, // NEU
    stressLevelDisplay, // NEU
    scenarioSelectedTitle, // NEU
    scenarioSelectedDescription; // NEU


// --- Backend Kommunikation ---
const BASE_URL = 'http://192.168.0.128:8004'; // WICHTIG: Anpassen, wenn Backend woanders läuft!

async function fetchData(endpoint, options = {}) {
    // (Funktion fetchData bleibt wie im letzten JS-Block, mit BASE_URL)
    if (!loadingIndicator) return null; 
    loadingIndicator.classList.remove('hidden');
    if (errorDisplay) errorDisplay.classList.add('hidden'); 
    console.log(`Fetching: ${BASE_URL}${endpoint}`, options); 

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, options);
        console.log(`Response Status: ${response.status} for ${endpoint}`);
        if (!response.ok) {
            let errorMsg = `HTTP error! Status: ${response.status}`;
            try { const errorData = await response.json(); errorMsg += ` - ${errorData.message || JSON.stringify(errorData)}`; } 
            catch (e) { errorMsg += ` - ${response.statusText}`; }
            throw new Error(errorMsg);
        }
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) { return await response.json(); } 
        else { console.warn(`Response from ${endpoint} is not JSON.`); return await response.text(); }
    } catch (e) {
        console.error(`Workspace error for ${endpoint}:`, e);
        handleError(e); return null; 
    } finally {
        if (loadingIndicator) loadingIndicator.classList.add('hidden');
    }
}

// --- UI Update Funktionen ---
function switchView(viewToShowId) {
    const views = [scenarioSelectionView, startView, interrogationView, accusationView, resultView]; // scenarioSelectionView hinzugefügt
    views.forEach(view => {
        if (view && view.id === viewToShowId) { view.classList.remove('hidden'); } 
        else if (view) { view.classList.add('hidden'); }
    });
     if (errorDisplay) errorDisplay.classList.add('hidden');
}

function displayMessage(message, type, speakerName = null) {
    // (Funktion displayMessage bleibt wie im letzten JS-Block)
    if (!message || typeof message !== 'string' || !dialogue) return; 
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `message-${type}`, 'mb-3', 'px-3', 'py-2', 'rounded-lg', 'max-w-[85%]', 'break-words'); 
    let prefix = "";
    if (type === 'player') { prefix = "Du: "; messageElement.classList.add('bg-detective-primary', 'text-white', 'ml-auto', 'text-right'); } 
    else if (type === 'suspect') { prefix = speakerName ? `${speakerName}: ` : "Verdächtiger: "; messageElement.classList.add('bg-detective-muted', 'text-detective-text', 'mr-auto', 'text-left'); } 
    else if (type === 'info') { messageElement.classList.add('bg-transparent', 'text-detective-info', 'italic', 'text-center', 'text-sm', 'mx-auto', 'max-w-full'); } 
    else if (type === 'error') { messageElement.classList.add('bg-red-900/50', 'text-detective-error', 'text-center', 'font-bold', 'mx-auto', 'max-w-full'); }
    messageElement.textContent = prefix + message;
    dialogue.appendChild(messageElement);
    dialogue.scrollTop = dialogue.scrollHeight; 
    if (speechEnabled && type === 'suspect') { speak(message); }
}

function updateQuestionsRemaining(count) {
     // (Funktion updateQuestionsRemaining bleibt wie im letzten JS-Block)
     if (questionsRemainingElement) {
        if (typeof count === 'number' && count >= 0) {
            questionsRemainingElement.textContent = `Noch ${count} Fragen für diesen Verdächtigen.`;
            if (count <= 0) { displayMessage("Du hast keine Fragen mehr für diesen Verdächtigen.", "info"); }
        } else { questionsRemainingElement.textContent = `Fragen übrig: ?`; }
     }
}

// *** NEU: Funktion zum Anzeigen des Herzschlags ***
function updateStressIndicator(bpm, level) {
     if (heartbeatDisplay && stressLevelDisplay) {
          heartbeatDisplay.textContent = `${bpm} bpm`;
          stressLevelDisplay.textContent = `[${level}]`;
          // Farbliche Anpassung basierend auf Level (optional)
          stressLevelDisplay.classList.remove('text-green-400', 'text-yellow-400', 'text-red-500');
          if (level === "Ruhe") stressLevelDisplay.classList.add('text-green-400');
          else if (level === "Angespannt") stressLevelDisplay.classList.add('text-yellow-400');
          else if (level === "Stress!") stressLevelDisplay.classList.add('text-red-500');
     }
}

// --- Spiel-Logik Funktionen ---

// *** NEU: Lade verfügbare Szenarien ***
async function loadAvailableScenarios() {
     const scenarios = await fetchData('/scenarios');
     if (scenarios && scenarioList) {
          scenarioList.innerHTML = ''; // Leeren
          if (scenarios.length === 0) {
               scenarioList.innerHTML = '<li class="text-center text-detective-info">Keine Szenarien gefunden.</li>';
               return;
          }
          scenarios.forEach(scenario => {
               const button = document.createElement('button');
               button.className = 'w-full p-4 bg-detective-muted hover:bg-gray-600 rounded-lg text-left transition duration-200';
               button.dataset.scenarioId = scenario.id; 
               button.innerHTML = `
                    <h3 class="font-semibold text-lg text-detective-text">${scenario.title}</h3>
                    <p class="text-sm text-detective-text/80">${scenario.description.substring(0, 100)}...</p> `;
               button.addEventListener('click', () => selectScenario(scenario.id));
               
               const listItem = document.createElement('li');
               listItem.appendChild(button);
               scenarioList.appendChild(listItem);
          });
          switchView('scenario-selection-view'); // Zeige Auswahl an
     } else {
          handleError(new Error("Verfügbare Szenarien konnten nicht geladen werden."));
     }
}

// *** NEU: Szenario auswählen und starten ***
async function selectScenario(scenarioId) {
    console.log(`Szenario ausgewählt: ${scenarioId}`);
    // Rufe Backend auf, um das Szenario zu "starten" und die Details zu bekommen
    const response = await fetchData(`/start_scenario/${scenarioId}`, { method: 'POST' });
    if (response && response.scenario) {
         currentScenarioId = response.scenario.id; // Speichere die ID des aktiven Szenarios
         scenarioData = response.scenario; // Speichere die Details des aktiven Szenarios
         
         // Aktualisiere Titel und Beschreibung in der Verdächtigen-Ansicht
         if(scenarioSelectedTitle) scenarioSelectedTitle.textContent = scenarioData.title;
         if(scenarioSelectedDescription) scenarioSelectedDescription.textContent = scenarioData.description;

         populateSuspectList(scenarioData.suspects); // Zeige Verdächtige für dieses Szenario
         switchView('start-view'); // Wechsle zur Verdächtigen-Auswahl
    } else {
         handleError(new Error(`Szenario ${scenarioId} konnte nicht gestartet werden.`));
    }
}


function populateSuspectList(suspects) {
     // (Funktion populateSuspectList bleibt wie im letzten JS-Block)
     if (!suspectList) return;
    suspectList.innerHTML = ''; 
    if (!suspects || suspects.length === 0) { suspectList.innerHTML = '<li class="text-center text-detective-info">Keine Verdächtigen gefunden.</li>'; return; }
    suspects.forEach(suspect => {
        const button = document.createElement('button');
        button.className = 'suspect-button w-full p-4 bg-detective-muted hover:bg-gray-600 rounded-lg text-left transition duration-200';
        button.dataset.suspectId = suspect.id; 
        button.innerHTML = `<h3 class="font-semibold text-lg text-detective-text">${suspect.name}</h3><p class="text-sm text-detective-text/80">${suspect.job}</p>`;
        button.addEventListener('click', () => startInterrogation(suspect.id));
        const listItem = document.createElement('li');
        listItem.appendChild(button);
        suspectList.appendChild(listItem);
    });
}

async function startInterrogation(suspectId) {
    currentSuspectId = suspectId;
    console.log(`Starte Befragung für ID: ${suspectId}`);
    // Zurücksetzen des Stress-Indikators beim Start der Befragung
    updateStressIndicator('--', '--'); // Setze auf Standard zurück
    switchView('interrogation-view');
    if (dialogue) dialogue.innerHTML = ''; 
    if (questionInput) questionInput.value = ''; 
    if (suspectInfo) suspectInfo.innerHTML = 'Lade Infos...'; 
    if (suspectName) suspectName.textContent = 'Verdächtiger wird geladen...';
    updateQuestionsRemaining('?'); 

    // Fordere Infos für diesen Verdächtigen im aktuellen Szenario an
    // Der Endpunkt benötigt jetzt eigentlich die scenario_id nicht mehr, da sie im Backend gespeichert ist
    // Aber zur Sicherheit könnte man sie mitschicken: /suspect/{currentScenarioId}/{suspectId}/info
    const data = await fetchData(`/suspect/${suspectId}/info`); 
    if (data) {
        if (suspectName) suspectName.textContent = `Befragung: ${data.name || 'Unbekannt'}`;
        if (suspectInfo) {
             suspectInfo.innerHTML = `
                 <p class="mb-1"><strong>Hintergrund:</strong> ${data.background || 'Keine Angabe'}</p>
                 <p><strong>Alibi:</strong> ${data.alibi || 'Keine Angabe'}</p>
             `;
        }
        updateQuestionsRemaining(data.questions_remaining !== undefined ? data.questions_remaining : MAX_QUESTIONS_PER_SUSPECT);
        if (data.starting_clue) {
             displayMessage(data.starting_clue, 'info');
        }
    } 
}

async function handleAskQuestion() {
    const question = questionInput.value.trim();
    if (!question || !currentSuspectId || !currentScenarioId) {
        if(!question) displayMessage("Bitte gib eine Frage ein.", "error");
        if(!currentSuspectId) displayMessage("Kein Verdächtiger ausgewählt.", "error");
        if(!currentScenarioId) displayMessage("Kein Szenario aktiv.", "error");
        return;
    }

    displayMessage(question, 'player'); 
    questionInput.value = ''; 
    questionInput.disabled = true; 
    if (sendButton) sendButton.disabled = true;
    if (speechButton) speechButton.disabled = true;

    // Sende Szenario-ID mit
    const response = await fetchData('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            question: question, 
            suspect_id: currentSuspectId,
            scenario_id: currentScenarioId // Füge Szenario-ID hinzu
         }) 
    });

    questionInput.disabled = false; 
    if (sendButton) sendButton.disabled = false;
    if (speechButton) speechButton.disabled = false;

    if (response) {
        if(response.error) {
             displayMessage(`Fehler vom Backend: ${response.error}`, 'error');
        } else {
            const suspect = scenarioData?.suspects?.find(s => s.id === currentSuspectId);
            const speakerName = suspect ? suspect.name : "Verdächtiger";
            
            displayMessage(response.answer || "Keine Antwort erhalten.", 'suspect', speakerName);
            if (response.stress_indicator) displayMessage(response.stress_indicator, 'info');
            if (response.getting_closer_hint) displayMessage(response.getting_closer_hint, 'info');
            if (response.questions_remaining !== undefined) updateQuestionsRemaining(response.questions_remaining);
            
            // *** NEU: Herzschlag/Stress aktualisieren ***
            if (response.heartbeat_bpm !== undefined && response.stress_level_text !== undefined) {
                 updateStressIndicator(response.heartbeat_bpm, response.stress_level_text);
            }
        }
    }
    questionInput.focus(); 
}

function changeSuspect() {
     if (scenarioData) {
          // Zeige die Verdächtigenliste des *aktuellen* Szenarios
         populateSuspectList(scenarioData.suspects); 
         switchView('start-view');
         currentSuspectId = null; 
     } else {
         handleError(new Error("Szenario-Daten nicht geladen."));
         loadAvailableScenarios(); // Zurück zur Szenario-Auswahl
     }
}

function startAccusation() {
     if (!scenarioData || !scenarioData.suspects || !accusationList) {
         handleError(new Error("Szenario-Daten nicht geladen."));
         return;
     }
     switchView('accusation-view');
     accusationList.innerHTML = ''; 
     let firstRadio = true;
     scenarioData.suspects.forEach(suspect => {
         // (Code zum Erstellen der Radio-Buttons bleibt gleich)
         const label = document.createElement('label');
         label.className = 'block p-3 bg-detective-muted hover:bg-gray-600 rounded-lg cursor-pointer transition duration-200 ring-2 ring-transparent peer-checked:ring-detective-primary';
         const radio = document.createElement('input');
         radio.type = 'radio'; radio.name = 'accusation'; radio.value = suspect.id;
         radio.className = 'mr-3 accent-detective-primary peer'; 
         radio.addEventListener('change', () => {
             document.querySelectorAll('#accusation-list label').forEach(l => l.classList.remove('ring-2', 'ring-detective-primary'));
             if(radio.checked) { label.classList.add('ring-2', 'ring-detective-primary'); }
         });
         label.appendChild(radio);
         label.appendChild(document.createTextNode(`${suspect.name} (${suspect.job})`));
         accusationList.appendChild(label);
     });
}

async function submitAccusation() {
    const selectedRadio = document.querySelector('#accusation-list input[name="accusation"]:checked');
    if (!selectedRadio) {
        handleError(new Error("Bitte wähle einen Verdächtigen aus.")); // Verwende handleError
        speak("Bitte wähle einen Verdächtigen aus.");
        return;
    }
    const accusedId = selectedRadio.value;
    console.log(`Beschuldige ID: ${accusedId} in Szenario ${currentScenarioId}`);

    // Sende Szenario-ID mit
    const result = await fetchData('/accuse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ suspect_id: accusedId, scenario_id: currentScenarioId }) 
    });

    if (result && resultView && resultHeading && resultMessage) {
        // (Code zur Ergebnisanzeige bleibt gleich)
        switchView('result-view');
        resultHeading.textContent = result.correct ? "Richtig!" : "Falsch!";
        resultMessage.textContent = result.message || "Ergebnis erhalten.";
        resultHeading.classList.toggle('text-detective-success', result.correct);
        resultHeading.classList.toggle('text-detective-error', !result.correct);
        speak(result.message); 
    } else if(!result) {
        handleError(new Error("Keine gültige Antwort vom Backend für Beschuldigung erhalten."));
    }
}

function newGame() {
    console.log("Neues Spiel gestartet.");
    // Gehe zurück zur Szenario-Auswahl statt Neuladen
    loadAvailableScenarios(); 
    // Setze interne Zustände zurück
    currentScenarioId = null;
    currentSuspectId = null;
    scenarioData = null;
}

function toggleTTS() {
     // (Funktion toggleTTS bleibt wie im letzten JS-Block)
    speechEnabled = !speechEnabled;
    if (ttsToggleButton) {
        ttsToggleButton.textContent = `Sprachausgabe: ${speechEnabled ? 'An' : 'Aus'}`;
        ttsToggleButton.classList.toggle('bg-green-600', speechEnabled);
        ttsToggleButton.classList.toggle('hover:bg-green-700', speechEnabled);
        ttsToggleButton.classList.toggle('bg-yellow-600', !speechEnabled);
        ttsToggleButton.classList.toggle('hover:bg-yellow-700', !speechEnabled);
    }
    console.log(`Sprachausgabe ${speechEnabled ? 'aktiviert' : 'deaktiviert'}.`);
    if (!speechEnabled && 'speechSynthesis' in window) { speechSynthesis.cancel(); } 
    else if (speechEnabled) { speak("Sprachausgabe aktiviert."); }
}

// --- Sprach-APIs (Funktionen initializeSpeechRecognition, startSpeechRecognition, speak unverändert) ---
function initializeSpeechRecognition() {
     // (Funktion initializeSpeechRecognition bleibt wie im letzten JS-Block)
     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
     if (!SpeechRecognition) { console.warn("Web Speech API (Recognition) nicht unterstützt."); if (speechButton) { speechButton.disabled = true; speechButton.title = "Spracherkennung nicht unterstützt"; speechButton.classList.add('opacity-50', 'cursor-not-allowed'); } return; }
     recognition = new SpeechRecognition();
     recognition.lang = 'de-DE'; recognition.interimResults = false; recognition.maxAlternatives = 1;
     recognition.onresult = (event) => { const speechResult = event.results[0][0].transcript; console.log('Spracherkennung Ergebnis:', speechResult); if (questionInput) questionInput.value = speechResult; };
     recognition.onerror = (event) => { console.error('Spracherkennung Fehler:', event.error); let errorMsg = 'Spracherkennung fehlgeschlagen.'; if (event.error === 'no-speech') errorMsg = 'Keine Sprache erkannt.'; else if (event.error === 'audio-capture') errorMsg = 'Mikrofonproblem.'; else if (event.error === 'not-allowed') errorMsg = 'Zugriff auf Mikrofon verweigert.'; handleError(new Error(errorMsg)); };
     recognition.onstart = () => { console.log("Spracherkennung gestartet..."); if (speechButton) speechButton.classList.add('recording', 'bg-red-600'); };
     recognition.onend = () => { console.log("Spracherkennung beendet."); if (speechButton) speechButton.classList.remove('recording', 'bg-red-600'); };
}

function startSpeechRecognition() {
    // (Funktion startSpeechRecognition bleibt wie im letzten JS-Block)
    if (!recognition) { console.error("Spracherkennung nicht initialisiert."); handleError(new Error('Spracherkennung nicht initialisiert.')); return; }
    try { recognition.stop(); recognition.start(); } catch (e) { console.warn("recognition.start() error:", e.message); setTimeout(() => { try { recognition.start(); } catch(e2) {} }, 100); }
}

function speak(text) {
     // (Funktion speak bleibt wie im letzten JS-Block)
    if (!speechEnabled || !text) return; 
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel(); 
        ttsUtterance = new SpeechSynthesisUtterance(text); 
        const setVoice = () => {
            const voices = speechSynthesis.getVoices();
            let germanVoice = voices.find(voice => voice.lang === 'de-DE');
            if (!germanVoice) germanVoice = voices.find(voice => voice.lang.startsWith('de'));
            if (germanVoice) { ttsUtterance.voice = germanVoice; /* console.log("Nutze TTS-Stimme:", germanVoice.name); */ } 
            else { console.warn("Keine de-DE Stimme für TTS gefunden."); ttsUtterance.lang = 'de-DE'; }
            ttsUtterance.rate = 1.0; ttsUtterance.pitch = 1.0; 
            speechSynthesis.speak(ttsUtterance);
        };
        if (speechSynthesis.getVoices().length === 0) { speechSynthesis.onvoiceschanged = setVoice; } 
        else { setVoice(); }
    } else { console.warn("Web Speech API (Synthesis) nicht unterstützt."); if (ttsToggleButton) ttsToggleButton.disabled = true; }
}

// --- Fehlerbehandlung ---
function handleError(error) {
     // (Funktion handleError bleibt wie im letzten JS-Block)
    console.error('Ein Fehler ist aufgetreten:', error);
    if(errorDisplay) {
        errorDisplay.textContent = `Fehler: ${error.message}`;
        errorDisplay.classList.remove('hidden');
        setTimeout(() => { errorDisplay.classList.add('hidden'); }, 5000);
    }
}

// --- Initialisierung beim Laden der Seite ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM geladen. Initialisiere Spiel...");
    
    // Cache DOM Elemente (alle IDs aus dem HTML)
    loadingIndicator = document.getElementById('loading');
    errorDisplay = document.getElementById('error');
    scenarioTitle = document.getElementById('scenario-title');
    scenarioSelectionView = document.getElementById('scenario-selection-view'); // NEU
    scenarioList = document.getElementById('scenario-list');                   // NEU
    startView = document.getElementById('start-view');
    suspectList = document.getElementById('suspect-list'); // Ist doppelt, aber ok
    scenarioSelectedTitle = document.getElementById('scenario-selected-title'); // NEU
    scenarioSelectedDescription = document.getElementById('scenario-selected-description'); // NEU
    interrogationView = document.getElementById('interrogation-view');
    suspectName = document.getElementById('suspect-name');
    suspectInfo = document.getElementById('suspect-info');
    stressIndicatorDisplay = document.getElementById('stress-indicator'); // NEU
    heartbeatDisplay = document.getElementById('heartbeat-display');       // NEU
    stressLevelDisplay = document.getElementById('stress-level-display'); // NEU
    dialogue = document.getElementById('dialogue');
    questionInput = document.getElementById('question-input');
    questionsRemainingElement = document.getElementById('questions-remaining');
    accusationView = document.getElementById('accusation-view');
    accusationList = document.getElementById('accusation-list');
    resultView = document.getElementById('result-view');
    resultHeading = document.getElementById('result-heading');
    resultMessage = document.getElementById('result-message');
    ttsToggleButton = document.getElementById('tts-toggle-button');
    sendButton = document.getElementById('send-button');
    speechButton = document.getElementById('speech-button');
    changeSuspectButton = document.getElementById('change-suspect-button');
    accuseButton = document.getElementById('accuse-button');
    accuseConfirmButton = document.getElementById('accuse-confirm-button');
    cancelAccusationButton = document.getElementById('cancel-accusation-button');
    newGameButton = document.getElementById('new-game-button');

    // Event Listener hinzufügen (prüfe Existenz)
    sendButton?.addEventListener('click', handleAskQuestion);
    speechButton?.addEventListener('click', startSpeechRecognition);
    changeSuspectButton?.addEventListener('click', changeSuspect);
    accuseButton?.addEventListener('click', startAccusation);
    accuseConfirmButton?.addEventListener('click', submitAccusation);
    cancelAccusationButton?.addEventListener('click', () => {
        if (currentSuspectId) startInterrogation(currentSuspectId); 
        else changeSuspect(); // Sollte zur Szenario-Auswahl gehen
    });
    newGameButton?.addEventListener('click', newGame);
    ttsToggleButton?.addEventListener('click', toggleTTS);
    questionInput?.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') { event.preventDefault(); handleAskQuestion(); }
    });

    initializeSpeechRecognition();
    
    // *** NEU: Lade verfügbare Szenarien statt direkt eines zu starten ***
    loadAvailableScenarios(); 
});
