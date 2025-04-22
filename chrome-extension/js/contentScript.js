/**
 * Someta Math Helper Widget
 * This content script injects a floating, draggable chat widget on any webpage
 */

// Configuration
const API_ENDPOINT = 'https://api.someta.com/socrato/chat'; // Replace with actual endpoint

// Store widget state
let widgetState = {
  minimized: false,
  position: { x: 20, y: 20 },
  isDragging: false,
  dragOffset: { x: 0, y: 0 },
  darkMode: false,
  messages: []
};

// Create and inject the widget
function createWidget() {
  const widgetHTML = `
    <div id="someta-widget" class="someta-widget">
      <div class="someta-header">
        <div class="someta-drag-handle">Someta Math Helper</div>
        <div class="someta-controls">
          <button id="someta-minimize" class="someta-btn someta-minimize" title="Minimize">−</button>
          <button id="someta-close" class="someta-btn someta-close" title="Close">×</button>
        </div>
      </div>
      
      <div id="someta-content" class="someta-content">
        <div id="someta-messages" class="someta-messages"></div>
        
        <div class="someta-input-area">
          <button id="someta-screenshot" class="someta-screenshot-btn" title="Take Screenshot">
            📷
          </button>
          <input type="text" id="someta-input" class="someta-input" placeholder="Type your math question...">
          <button id="someta-send" class="someta-send-btn">Send</button>
        </div>
      </div>
      
      <div id="someta-minimized" class="someta-minimized hidden">
        <span>Someta</span>
      </div>
    </div>
  `;
  
  // Create widget container
  const widgetContainer = document.createElement('div');
  widgetContainer.id = 'someta-container';
  widgetContainer.innerHTML = widgetHTML;
  document.body.appendChild(widgetContainer);
  
  // Position the widget
  const widget = document.getElementById('someta-widget');
  widget.style.left = `${widgetState.position.x}px`;
  widget.style.top = `${widgetState.position.y}px`;
  
  // If starting minimized, toggle minimized state
  chrome.storage.sync.get(['startMinimized', 'darkMode'], (result) => {
    if (result.startMinimized) {
      toggleMinimize();
    }
    
    if (result.darkMode) {
      widgetState.darkMode = true;
      widget.classList.add('someta-dark-mode');
    }
  });
  
  // Initialize event listeners
  initializeEventListeners();
}

// Initialize widget event listeners
function initializeEventListeners() {
  // Dragging functionality
  const dragHandle = document.querySelector('.someta-drag-handle');
  const widget = document.getElementById('someta-widget');
  
  dragHandle.addEventListener('mousedown', (e) => {
    widgetState.isDragging = true;
    widgetState.dragOffset.x = e.clientX - widget.getBoundingClientRect().left;
    widgetState.dragOffset.y = e.clientY - widget.getBoundingClientRect().top;
    dragHandle.style.cursor = 'grabbing';
  });
  
  document.addEventListener('mousemove', (e) => {
    if (widgetState.isDragging) {
      widget.style.left = `${e.clientX - widgetState.dragOffset.x}px`;
      widget.style.top = `${e.clientY - widgetState.dragOffset.y}px`;
    }
  });
  
  document.addEventListener('mouseup', () => {
    if (widgetState.isDragging) {
      widgetState.isDragging = false;
      widgetState.position.x = parseInt(widget.style.left);
      widgetState.position.y = parseInt(widget.style.top);
      dragHandle.style.cursor = 'grab';
      
      // Save position
      chrome.storage.sync.set({ widgetPosition: widgetState.position });
    }
  });
  
  // Button actions
  document.getElementById('someta-minimize').addEventListener('click', toggleMinimize);
  document.getElementById('someta-close').addEventListener('click', closeWidget);
  document.getElementById('someta-minimized').addEventListener('click', toggleMinimize);
  document.getElementById('someta-send').addEventListener('click', sendMessage);
  document.getElementById('someta-screenshot').addEventListener('click', takeScreenshot);
  
  // Handle enter key in input
  document.getElementById('someta-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
}

// Toggle minimized state
function toggleMinimize() {
  const content = document.getElementById('someta-content');
  const minimized = document.getElementById('someta-minimized');
  
  widgetState.minimized = !widgetState.minimized;
  
  if (widgetState.minimized) {
    content.classList.add('hidden');
    minimized.classList.remove('hidden');
  } else {
    content.classList.remove('hidden');
    minimized.classList.add('hidden');
  }
}

// Close the widget
function closeWidget() {
  const widget = document.getElementById('someta-container');
  widget.remove();
}

// Send a message
function sendMessage() {
  const input = document.getElementById('someta-input');
  const message = input.value.trim();
  
  if (message) {
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    input.value = '';
    
    // Send to backend
    sendToBackend(message);
  }
}

// Add a message to the chat
function addMessageToChat(sender, text) {
  const messagesContainer = document.getElementById('someta-messages');
  const messageElement = document.createElement('div');
  messageElement.className = `someta-message someta-${sender}-message`;
  
  // Format message
  messageElement.innerHTML = `<span class="someta-message-text">${text}</span>`;
  
  // Add to container
  messagesContainer.appendChild(messageElement);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  // Save to state
  widgetState.messages.push({ sender, text });
}

// Send message to backend
function sendToBackend(message, screenshot = null) {
  // Show loading message
  addMessageToChat('system', 'Thinking...');
  
  // Prepare data
  const data = {
    message,
    screenshot
  };
  
  // Get API key from storage
  chrome.storage.sync.get(['apiKey'], (result) => {
    // Headers with optional API key
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (result.apiKey) {
      headers['Authorization'] = `Bearer ${result.apiKey}`;
    }
    
    // Send message via background script
    chrome.runtime.sendMessage({
      action: 'sendToBackend',
      data: data,
      headers: headers
    }, (response) => {
      // Remove the loading message
      const messagesContainer = document.getElementById('someta-messages');
      const loadingMessage = messagesContainer.lastChild;
      messagesContainer.removeChild(loadingMessage);
      
      if (response && response.success) {
        // Add response to chat
        addMessageToChat('assistant', response.data);
      } else {
        // Show error
        addMessageToChat('system', 'Error: Could not get a response. Please try again.');
      }
    });
  });
}

// Take a screenshot
function takeScreenshot() {
  // Minimize widget temporarily for clean screenshot
  const widget = document.getElementById('someta-widget');
  widget.style.display = 'none';
  
  // Notify user
  addMessageToChat('system', 'Taking screenshot...');
  
  // Send message to background script to take screenshot
  chrome.runtime.sendMessage({ action: 'takeScreenshot' }, (response) => {
    // Show widget again
    widget.style.display = 'block';
    
    if (response && response.success) {
      // Show screenshot preview
      addMessageToChat('system', `<img src="${response.dataUrl}" class="someta-screenshot-preview">`);
      
      // Send screenshot to backend
      sendToBackend('I need help with this math problem:', response.dataUrl);
    } else {
      // Show error
      addMessageToChat('system', 'Error: Could not take screenshot. Please try again.');
    }
  });
}

// Initialize the widget when the page loads
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'activateWidget') {
    if (!document.getElementById('someta-container')) {
      createWidget();
    }
    sendResponse({ success: true });
  }
  return true;
});

// Check if we should auto-activate
chrome.storage.sync.get(['autoActivate'], (result) => {
  if (result.autoActivate) {
    createWidget();
  }
}); 