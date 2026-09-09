// Chrome Extension Background Service Worker
// Handles communication, caching, and background processing

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('TrustShield AI extension installed');
  
  // Initialize default settings
  chrome.storage.sync.set({
    apiEndpoint: 'http://localhost:8000',
    enableBackendAnalysis: false,
    riskThreshold: 50,
    privacyMode: true,
    extensionVersion: chrome.runtime.getManifest().version
  });
});

// Promise helper for chrome.storage
function getStorage(keys) {
  return new Promise((resolve) => {
    chrome.storage.sync.get(keys, resolve);
  });
}

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'ANALYZE_EMAIL') {
    analyzeEmail(request.data, sendResponse);
    return true; // Keep channel open for async response
  }
  
  if (request.type === 'REPORT_PHISHING') {
    reportPhishing(request.data, sendResponse);
    return true;
  }
  
  if (request.type === 'GET_SETTINGS') {
    chrome.storage.sync.get(null, (settings) => {
      sendResponse({ success: true, data: settings });
    });
    return true;
  }
});

/**
 * Analyze email by sending to backend
 */
async function analyzeEmail(emailData, sendResponse) {
  try {
    // Get settings
    const settings = await getStorage({ apiEndpoint: 'http://localhost:8000' });
    const apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';
    
    // Send to backend API
    const response = await fetch(`${apiEndpoint}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Extension-Id': chrome.runtime.id,
        'X-Extension-Version': chrome.runtime.getManifest().version
      },
      body: JSON.stringify(emailData)
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const analysis = await response.json();
    
    // Cache result
    cacheAnalysisResult(emailData.extractedAt, analysis);
    
    // Send response back to content script
    sendResponse({
      success: true,
      analysis: analysis.data
    });
    
  } catch (error) {
    console.error('Analysis error:', error);
    sendResponse({
      success: false,
      error: error.message
    });
  }
}

/**
 * Report phishing email
 */
async function reportPhishing(reportData, sendResponse) {
  try {
    const settings = await getStorage({ apiEndpoint: 'http://localhost:8000' });
    const apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';
    
    const response = await fetch(`${apiEndpoint}/api/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Extension-Id': chrome.runtime.id
      },
      body: JSON.stringify(reportData)
    });
    
    const result = await response.json();
    
    sendResponse({
      success: response.ok,
      data: result
    });
    
  } catch (error) {
    sendResponse({
      success: false,
      error: error.message
    });
  }
}

/**
 * Cache analysis result for offline use
 */
function cacheAnalysisResult(timestamp, analysis) {
  chrome.storage.local.get({ analysisCache: [] }, (result) => {
    const cache = result.analysisCache || [];
    
    // Add new result
    cache.unshift({
      timestamp,
      analysis,
      cachedAt: new Date().toISOString()
    });
    
    // Keep only last 1000 results
    if (cache.length > 1000) {
      cache.pop();
    }
    
    chrome.storage.local.set({ analysisCache: cache });
  });
}

// Handle badge updates
function updateBadge(riskLevel) {
  const colors = {
    'LOW': '#388e3c',
    'MEDIUM': '#fbc02d',
    'HIGH': '#f57c00',
    'CRITICAL': '#d32f2f'
  };
  
  chrome.action.setBadgeBackgroundColor({
    color: colors[riskLevel] || '#757575'
  });
  
  if (riskLevel !== 'LOW') {
    chrome.action.setBadgeText({ text: '!' });
  }
}

// Periodic threat intelligence update (every 24 hours)
chrome.alarms.create('updateThreatIntel', { periodInMinutes: 1440 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'updateThreatIntel') {
    updateThreatIntelligence();
  }
});

async function updateThreatIntelligence() {
  try {
    const settings = await getStorage({ apiEndpoint: 'http://localhost:8000' });
    const apiEndpoint = settings.apiEndpoint || 'http://localhost:8000';
    
    const response = await fetch(`${apiEndpoint}/api/threat-intelligence`);
    const threatData = await response.json();
    
    // Cache threat intelligence
    chrome.storage.local.set({
      threatIntelligence: threatData.data,
      threatIntelUpdatedAt: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Threat intelligence update failed:', error);
  }
}

console.log('TrustShield AI: Background service worker loaded');
