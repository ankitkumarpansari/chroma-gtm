// LinkedIn Sales Navigator Company Adder - Background Service Worker

console.log('🎯 Sales Nav Company Adder: Background service worker started');

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Extension installed');
    
    // Initialize storage
    chrome.storage.local.set({
      results: [],
      settings: {
        autoSave: true,
        skipSaved: true,
        randomDelay: true
      }
    });
  }
});

// Handle messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getTab') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      sendResponse({ tab: tabs[0] });
    });
    return true;
  }
  
  if (request.action === 'openSalesNav') {
    chrome.tabs.create({ url: 'https://www.linkedin.com/sales/home' });
    sendResponse({ success: true });
    return true;
  }
});

// Keep service worker alive
chrome.alarms.create('keepAlive', { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'keepAlive') {
    console.log('Service worker keep-alive ping');
  }
});

