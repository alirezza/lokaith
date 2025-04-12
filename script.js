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

function showStartView(scenarioData) {
  // Show start view with suspects list
  console.log('Showing start view');
  const scenarioTitle = document.getElementById('scenario-title');
  const scenarioDescription = document.getElementById('scenario-description');
  const suspectsList = document.getElementById('suspects-list');
  const startView = document.getElementById('start-view');
  const interrogationView = document.getElementById('interrogation-view');
  const accusationView = document.getElementById('accusation-view');
  const resultView = document.getElementById('result-view');

  if (scenarioTitle && scenarioDescription && suspectsList && startView && interrogationView && accusationView && resultView && scenarioData) {
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
      listItem.querySelector('button').addEventListener('click', function() {
        showInterrogationView(suspect.id);
      });
      suspectsList.appendChild(listItem);
    });
    interrogationView.style.display = 'none';
    accusationView.style.display = 'none';
    resultView.style.display = 'none';
    startView.style.display = 'block';
  } else {
    console.error("One or more elements not found or scenario data is missing.");
  }
}

async function showInterrogationView(suspectId) {
    console.log(`Showing interrogation view for suspect ID: ${suspectId}`);
    currentSuspectId = suspectId;
    const startView = document.getElementById('start-view');
    const interrogationView = document.getElementById('interrogation-view');
    const accusationView = document.getElementById('accusation-view');
    const resultView = document.getElementById('result-view');
    const suspectInfoContainer = document.getElementById('suspect-info');
    const dialogue = document.getElementById('dialogue');
    const questionInput = document.getElementById('question-input');
    const questionsRemainingElement = document.getElementById('questions-remaining');
  
    if (startView && interrogationView && accusationView && resultView && suspectInfoContainer && dialogue && questionInput && questionsRemainingElement) {
      startView.style.display = 'none';
      accusationView.style.display = 'none';
      resultView.style.display = 'none';
      interrogationView.style.display = 'block';
  
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
          // Fetch initial data for questions remaining or set a default value
          const initialData = await askQuestion("", suspectId); // Empty question to get initial state
          if (initialData && initialData.questions_remaining !== undefined) {
              questionsRemainingElement.textContent = `Questions Remaining: ${initialData.questions_remaining}`;
          } else {
              questionsRemainingElement.textContent = 'Questions Remaining: N/A'; // Or some default value
          }
        }
      } catch (error) {
        handleError(error);
      }
    } else {
      console.error("One or more elements not found in interrogation view.");
    }
  }
  

function showAccusationView(scenarioData) {
  console.log('Showing accusation view');
  const startView = document.getElementById('start-view');
  const interrogationView = document.getElementById('interrogation-view');
  const accusationView = document.getElementById('accusation-view');
  const resultView = document.getElementById('result-view');
  const accusationList = document.getElementById('accusation-list');

  if (startView && interrogationView && accusationView && resultView && accusationList) {
    startView.style.display = 'none';
    interrogationView.style.display = 'none';
    resultView.style.display = 'none';
    accusationView.style.display = 'block';

    accusationList.innerHTML = '';
    scenarioData.suspects.forEach(suspect => {
      const listItem = document.createElement('li');
      listItem.innerHTML = `
        <button class="w-full p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-left" data-suspect-id="${suspect.id}">
          <h3 class="font-semibold">${suspect.name}</h3>
        </button>
      `;
      listItem.querySelector('button').addEventListener('click', function() {
        // Remove 'selected' class from previously selected item
        document.querySelectorAll('#accusation-list li button').forEach(el => el.classList.remove('selected', 'bg-green-700', 'hover:bg-green-600'));
        // Add 'selected' class to the clicked item
        this.classList.add('selected', 'bg-green-700', 'hover:bg-green-600');
      });
      accusationList.appendChild(listItem);
    });
  }
}

function showResultView(result) {
  console.log('Showing result view');
  const startView = document.getElementById('start-view');
  const interrogationView = document.getElementById('interrogation-view');
  const accusationView = document.getElementById('accusation-view');
  const resultView = document.getElementById('result-view');
  const resultMessage = document.getElementById('result-message');

  if (startView && interrogationView && accusationView && resultView && resultMessage) {
    startView.style.display = 'none';
    interrogationView.style.display = 'none';
    accusationView.style.display = 'none';
    resultView.style.display = 'block';

    resultMessage.textContent = result.message;
  }
}

function displayMessage(message, type) {
  const dialogue = document.getElementById('dialogue');
  if (dialogue) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `message-${type}`);
    messageElement.textContent = message;
    dialogue.appendChild(messageElement);
    dialogue.scrollTop = dialogue.scrollHeight; // Auto-scroll
    if (speechEnabled && type === 'suspect') {
      speak(message);
    }
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
  displayMessage(`Error: ${error.message}`, 'info');
  // Optionally, update UI to indicate an error state
}

// Initialize the game
async function initializeGame() {
  console.log('Initializing game');
  try {
    const scenarioData = await fetchScenario();
    if (scenarioData) {
      showStartView(scenarioData);
      // Store scenarioData for later use in accusation phase
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
          try {
            const response = await askQuestion(question, currentSuspectId);
            updateUI(response);
          } catch (error) {
            handleError(error);
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
  const accuseConfirmButton = document.getElementById('accuse-confirm-button');
  if (accuseConfirmButton) {
    accuseConfirmButton.addEventListener('click', async () => {
      const selectedSuspect = document.querySelector('#accusation-list li button.selected');
      if (selectedSuspect) {
        const suspectId = selectedSuspect.dataset.suspectId;
        try {
          const result = await accuseSuspect(suspectId);
          showResultView(result);
        } catch (error) {
          handleError(error);
        }
      } else {
        handleError(new Error("Please select a suspect to accuse."));
      }
    });
  }
  
    // New Game button event listener (in result view)
  const newGameButton = document.getElementById('new-game-button');
  if (newGameButton) {
    newGameButton.addEventListener('click', () => {
      initializeGame(); // Restart the game
    });
  }

  const toggleSpeechButton = document.getElementById('toggle-speech-button');
  if (toggleSpeechButton) {
    toggleSpeechButton.addEventListener('click', () => {
      speechEnabled = !speechEnabled;
      toggleSpeechButton.textContent = speechEnabled ? 'Disable Speech' : 'Enable Speech';
    });
  }
});