// script.js

let currentSuspectId = null;
let speechEnabled = false; // Initially disable speech output

// Placeholder functions for API calls
async function fetchScenario() {
  try {
    const response = await fetch('/scenario');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    handleError(error);
  }
}

async function fetchSuspectInfo(id) {
  try {
    const response = await fetch(`/suspect/${id}/info`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    handleError(error);
  }
}

async function askQuestion(question, suspectId) {
  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: question, suspectId: suspectId }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    handleError(error);
  }
}

async function accuseSuspect(suspectId) {
  try {
    const response = await fetch('/accuse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ suspectId: suspectId }),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    handleError(error);
  }
}

// Placeholder functions for UI updates and interactions
function updateUI(data) {
  // Implement UI update logic here
  console.log('Updating UI with:', data);
    if (data.answer) {
    displayMessage(data.answer, "suspect");
  }
  if (data.questions_remaining !== undefined) {
    const questionsRemainingElement = document.getElementById('questions-remaining');
    if (questionsRemainingElement) {
        questionsRemainingElement.textContent = `Questions Remaining: ${data.questions_remaining}`;
    }
  }
}

// Helper function to get DOM elements and handle errors
function getElement(id) {
    const element = document.getElementById(id);
    if (!element) {
        throw new Error(`Element with ID "${id}" not found.`);
    }
    return element;
}

let selectedSuspectId = null;

function showStartView(scenarioData) {
    console.log('Showing start view');

    const [startView, interrogationView, accusationView, resultView, scenarioTitle, scenarioDescription, suspectsList, errorDisplay] = [
        'start-view', 'interrogation-view', 'accusation-view', 'result-view', 'scenario-title', 'scenario-description', 'suspects-list', 'error'
    ].map(getElement);

    if (!scenarioData) {
        throw new Error("Scenario data is missing.");
    }

    scenarioTitle.textContent = scenarioData.title;
    scenarioDescription.textContent = scenarioData.description;

    suspectsList.innerHTML = ''; // Clear existing list items
    scenarioData.suspects.forEach(suspect => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            <button class="w-full p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-left" data-suspect-id="${suspect.id}">
                <h3 class="font-semibold">${suspect.name}</h3>
                <p class="text-gray-300">${suspect.job}</p>
            </button>
        `;
        listItem.querySelector('button').addEventListener('click', () => {
            showInterrogationView(suspect.id);
        });
        suspectsList.appendChild(listItem);
    });

    // Use CSS classes for view management
    startView.classList.remove('hidden');
    [interrogationView, accusationView, resultView].forEach(view => view.classList.add('hidden'));
    errorDisplay.classList.add('hidden');
}

async function showInterrogationView(suspectId) {
    console.log(`Showing interrogation view for suspect ID: ${suspectId}`);
    currentSuspectId = suspectId;

    const [startView, interrogationView, accusationView, resultView, suspectInfoContainer, dialogue, questionInput, questionsRemainingElement, errorDisplay] = [
        'start-view', 'interrogation-view', 'accusation-view', 'result-view', 'suspect-info', 'dialogue', 'question-input', 'questions-remaining', 'error'
    ].map(getElement);

    // Use CSS classes for view management
    interrogationView.classList.remove('hidden');
    [startView, accusationView, resultView].forEach(view => view.classList.add('hidden'));
    errorDisplay.classList.add('hidden');

    // Clear previous content
    suspectInfoContainer.innerHTML = '';
    dialogue.innerHTML = '';
    questionInput.value = '';
    questionsRemainingElement.textContent = 'Loading...';

    try {
        const suspectInfo = await fetchSuspectInfo(suspectId);
        if (suspectInfo) {
            suspectInfoContainer.innerHTML = `
                <h2 class="text-2xl font-bold">${suspectInfo.name}</h2>
                <p class="text-gray-300">${suspectInfo.background}</p>
                <p class="text-gray-300 mt-2"><strong>Alibi:</strong> ${suspectInfo.alibi}</p>
            `;
            questionsRemainingElement.textContent = `Questions Remaining: ${suspectInfo.questions_remaining}`;
        }
    } catch (error) {
        handleError(error);
    }
}

function showAccusationView(scenarioData) {
    console.log('Showing accusation view');

    const [startView, interrogationView, accusationView, resultView, accusationList, errorDisplay] = [
        'start-view', 'interrogation-view', 'accusation-view', 'result-view', 'accusation-list', 'error'
    ].map(getElement);

    // Use CSS classes for view management
    accusationView.classList.remove('hidden');
    [startView, interrogationView, resultView].forEach(view => view.classList.add('hidden'));
    errorDisplay.classList.add('hidden');

    accusationList.innerHTML = '';
    selectedSuspectId = null; // Reset selection

    scenarioData.suspects.forEach(suspect => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `
            <button class="w-full p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-left" data-suspect-id="${suspect.id}">
                <h3 class="font-semibold">${suspect.name}</h3>
            </button>
        `;
        const button = listItem.querySelector('button');
        button.addEventListener('click', function () {
            // Remove 'selected' class from previously selected item
            document.querySelectorAll('#accusation-list li button').forEach(el => el.classList.remove('selected', 'bg-green-700', 'hover:bg-green-600'));
            // Add 'selected' class to the clicked item
            this.classList.add('selected', 'bg-green-700', 'hover:bg-green-600');
            selectedSuspectId = suspect.id; // Track selected suspect
        });
        accusationList.appendChild(listItem);
    });
}

function showResultView(result) {
    console.log('Showing result view');

    const [startView, interrogationView, accusationView, resultView, resultMessage, errorDisplay] = [
        'start-view', 'interrogation-view', 'accusation-view', 'result-view', 'result-message', 'error'
    ].map(getElement);

    // Use CSS classes for view management
    resultView.classList.remove('hidden');
    [startView, interrogationView, accusationView].forEach(view => view.classList.add('hidden'));
    errorDisplay.classList.add('hidden');

    resultMessage.textContent = result.message;
}

function displayMessage(message, type) {
    const dialogue = getElement('dialogue');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `message-${type}`);
    messageElement.textContent = message;
    dialogue.appendChild(messageElement);
    dialogue.scrollTop = dialogue.scrollHeight; // Auto-scroll
    if (speechEnabled && type === 'suspect') {
        speak(message);
    }
}

// Placeholder functions for speech interaction
function startSpeechRecognition() {
  console.log('Starting speech recognition');
  // Implement speech recognition using Web Speech API
  if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US'; // Set the language
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = function(event) {
      const speechResult = event.results[0][0].transcript;
      console.log('Speech result:', speechResult);
      document.getElementById('question-input').value = speechResult;
    };

    recognition.onerror = function(event) {
      console.error('Speech recognition error:', event.error);
      handleError(new Error('Speech recognition failed.'));
    };

    recognition.start();
  } else {
    handleError(new Error('Speech recognition is not supported in this browser.'));
  }
}

function speak(text) {
  console.log('Speaking:', text);
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    // You can customize voice, rate, pitch, etc.
    speechSynthesis.speak(utterance);
  } else {
    handleError(new Error('Speech synthesis is not supported in this browser.'));
  }
}

// Helper function for error handling
function handleError(error) {
  console.error('Error:', error);
  const errorDisplay = getElement('error');
  errorDisplay.textContent = `Error: ${error.message}`;
}

// Initialize the game
async function initializeGame() {
  console.log('Initializing game');
  try {
    const scenarioData = await fetchScenario();
    if (scenarioData) {
      window.scenarioData = scenarioData; 
    }
  } catch (error) {
    handleError(error);
  }
}


// Event listeners (ensure DOM is loaded)
document.addEventListener('DOMContentLoaded', () => {
  initializeGame();

  // Start view event listeners are now in showStartView
    if (window.scenarioData) {
  // Interrogation view event listeners
  const sendButton = document.getElementById('send-button');
  const speechButton = document.getElementById('speech-button');
  const changeSuspectButton = document.getElementById('change-suspect-button');
  const accuseButton = document.getElementById('accuse-button');
  const questionInput = document.getElementById('question-input');

  if (sendButton) {
    sendButton.addEventListener('click', async () => {
      if (currentSuspectId) {
        const question = questionInput.value;
        if (question.trim() !== "") {
                    displayMessage(`You: ${question}`, 'player');
                    questionInput.value = ""; // Clear input after sending
                    const response = await askQuestion(question, currentSuspectId);
                    if (response) {
                        updateUI(response);
                    }
        }
      } else {
        handleError(new Error("No suspect selected."));
      }
    });
  }

  if (speechButton) {
    speechButton.addEventListener('click', startSpeechRecognition);
  }

  if (changeSuspectButton) {
    changeSuspectButton.addEventListener('click', () => {
      if (window.scenarioData) {
        showStartView(window.scenarioData);
      } else {
        handleError(new Error("Scenario data not loaded."));
      }
    });
  }

  if (accuseButton) {
    accuseButton.addEventListener('click', () => {
      if (window.scenarioData) {
        showAccusationView(window.scenarioData);
      } else {
        handleError(new Error("Scenario data not loaded."));
      }
    });
  }
  
  // Accusation view event listener (for accusing a suspect)
    getElement('accuse-confirm-button').addEventListener('click', async () => {
        if (selectedSuspectId) {
            try {
                const result = await accuseSuspect(selectedSuspectId);
                showResultView(result);
            } catch (error) {
                handleError(error);
            }
        } else {
            displayMessage("Please select a suspect to accuse.", 'info');
        }
    });
    getElement('new-game-button').addEventListener('click', () => {
        window.location.reload();
    });
  }

  const toggleSpeechButton = document.getElementById('toggle-speech-button');
  if (toggleSpeechButton) {
    toggleSpeechButton.addEventListener('click', () => {
      speechEnabled = !speechEnabled;
      toggleSpeechButton.textContent = speechEnabled ? 'Disable Speech' : 'Enable Speech';
    });
  }
      showStartView(window.scenarioData);
  });
