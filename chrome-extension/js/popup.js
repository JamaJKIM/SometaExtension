/**
 * Someta Math Helper - Popup Script
 * 
 * Handles interactions within the extension popup
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize button handlers
  initializeButtons();
  
  // Load saved options
  loadSavedOptions();
});

// Initialize button click handlers
function initializeButtons() {
  // Activate button
  document.getElementById('activateBtn').addEventListener('click', () => {
    // Send message to the active tab to show the widget
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'activateWidget' }, (response) => {
        // If content script is not yet loaded, inject it
        if (chrome.runtime.lastError) {
          chrome.scripting.executeScript({
            target: { tabId: tabs[0].id },
            files: ['js/contentScript.js']
          }, () => {
            // After injecting, try sending the message again
            setTimeout(() => {
              chrome.tabs.sendMessage(tabs[0].id, { action: 'activateWidget' });
            }, 200);
          });
          
          chrome.scripting.insertCSS({
            target: { tabId: tabs[0].id },
            files: ['css/widget.css']
          });
        }
        
        // Close the popup
        window.close();
      });
    });
  });
  
  // Save options button
  document.getElementById('saveOptions').addEventListener('click', saveOptions);
}

// Load saved options from storage
function loadSavedOptions() {
  chrome.storage.sync.get(
    {
      apiKey: '',
      startMinimized: false,
      darkMode: false,
      autoActivate: false
    }, 
    (items) => {
      document.getElementById('apiKeyInput').value = items.apiKey;
      document.getElementById('startMinimized').checked = items.startMinimized;
      document.getElementById('darkMode').checked = items.darkMode;
    }
  );
}

// Save options to storage
function saveOptions() {
  const apiKey = document.getElementById('apiKeyInput').value;
  const startMinimized = document.getElementById('startMinimized').checked;
  const darkMode = document.getElementById('darkMode').checked;
  
  chrome.storage.sync.set(
    {
      apiKey: apiKey,
      startMinimized: startMinimized,
      darkMode: darkMode
    },
    () => {
      // Show a saved message
      const saveBtn = document.getElementById('saveOptions');
      const originalText = saveBtn.textContent;
      
      saveBtn.textContent = 'Saved!';
      saveBtn.disabled = true;
      
      setTimeout(() => {
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
      }, 1500);
    }
  );
} 