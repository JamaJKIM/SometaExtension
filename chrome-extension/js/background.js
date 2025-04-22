/**
 * Someta Math Helper - Background Script
 * 
 * Handles background tasks like API communications and screenshot capturing
 */

// Configuration
const API_ENDPOINT = 'https://someta-api.onrender.com/socrato/chat'; // Replace with your actual deployed endpoint

// Listen for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'sendToBackend':
      sendToBackend(message.data, message.headers, sendResponse);
      return true; // Keep the message channel open for async response
      
    case 'takeScreenshot':
      takeScreenshot(sender.tab.id, sendResponse);
      return true; // Keep the message channel open for async response
  }
});

// Listen for extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Check if we're on a webpage that we can inject our content into
  if (tab.url.startsWith('http')) {
    chrome.tabs.sendMessage(tab.id, { action: 'activateWidget' }, (response) => {
      // If the content script hasn't been loaded yet, we need to inject it
      if (chrome.runtime.lastError) {
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ['js/contentScript.js']
        }, () => {
          // After injecting, we can send the message again
          setTimeout(() => {
            chrome.tabs.sendMessage(tab.id, { action: 'activateWidget' });
          }, 200);
        });
        
        chrome.scripting.insertCSS({
          target: { tabId: tab.id },
          files: ['css/widget.css']
        });
      }
    });
  }
});

/**
 * Send data to the backend API
 * @param {Object} data - The data to send
 * @param {Object} headers - Headers to include in the request
 * @param {Function} sendResponse - Function to call with the response
 */
function sendToBackend(data, headers, sendResponse) {
  fetch(API_ENDPOINT, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(data)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    sendResponse({ success: true, data: data.response });
  })
  .catch(error => {
    console.error('API Error:', error);
    sendResponse({ success: false, error: error.message });
  });
}

/**
 * Take a screenshot of the current tab
 * @param {number} tabId - The ID of the tab to screenshot
 * @param {Function} sendResponse - Function to call with the response
 */
function takeScreenshot(tabId, sendResponse) {
  chrome.tabs.captureVisibleTab({ format: 'png' }, (dataUrl) => {
    if (chrome.runtime.lastError) {
      console.error('Screenshot error:', chrome.runtime.lastError);
      sendResponse({ success: false, error: chrome.runtime.lastError.message });
    } else {
      sendResponse({ success: true, dataUrl: dataUrl });
    }
  });
} 