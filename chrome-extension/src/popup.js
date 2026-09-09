const app = document.getElementById('app');
app.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
app.style.margin = '0';
app.style.padding = '0';
app.style.minWidth = '340px';
app.style.backgroundColor = '#f8fafc';
app.style.color = '#334155';

app.innerHTML = `
  <div style="background-color: white; padding: 16px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 16px;">
    <img src="/icons/icon.png" alt="TrustShield" style="width: 48px; height: 48px; object-fit: contain;" />
    <div>
      <h2 style="margin: 0; font-size: 16px; font-weight: 600; color: #0f172a;">TrustShield AI</h2>
      <p style="margin: 0; font-size: 12px; color: #64748b;">Live Phishing Protection</p>
    </div>
  </div>
  
  <div style="padding: 16px; display: flex; flex-direction: column; gap: 12px;">
    <div id="stats-container" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
      <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center;">
        <div style="font-size: 11px; color: #64748b; font-weight: 500; text-transform: uppercase;">Analyzed</div>
        <div id="stat-analyzed" style="font-size: 20px; font-weight: 700; color: #3b82f6; margin-top: 4px;">--</div>
      </div>
      <div style="background: white; border: 1px solid #fecaca; border-radius: 8px; padding: 12px; text-align: center;">
        <div style="font-size: 11px; color: #ef4444; font-weight: 600; text-transform: uppercase;">Blocked</div>
        <div id="stat-blocked" style="font-size: 20px; font-weight: 700; color: #ef4444; margin-top: 4px;">--</div>
      </div>
      <div style="grid-column: span 2; background: white; border: 1px solid #fef08a; border-radius: 8px; padding: 12px; text-align: center;">
        <div style="font-size: 11px; color: #d97706; font-weight: 600; text-transform: uppercase;">Phishing Detected</div>
        <div id="stat-phishing" style="font-size: 24px; font-weight: 700; color: #d97706; margin-top: 4px;">--</div>
      </div>
    </div>

    <div id="status" style="margin-top: 4px; padding: 10px; border-radius: 6px; background: #f1f5f9; font-size: 12px; display: flex; align-items: center; justify-content: space-between;">
      <span style="color: #64748b;">Backend Status</span>
      <span id="connection-status" style="font-weight: 600; color: #94a3b8;">Connecting...</span>
    </div>
    
    <button id="check-gmail" style="margin-top: 8px; width: 100%; padding: 12px; border: none; border-radius: 8px; background: #2563eb; color: white; font-weight: 600; font-size: 13px; cursor: pointer; transition: background 0.2s;">
      Scan Current Gmail Tab
    </button>
    <div id="result" style="font-size: 12px; color: #64748b; text-align: center; min-height: 18px;"></div>
  </div>
`;

const statusEl = document.getElementById('connection-status');
const resultEl = document.getElementById('result');
const statAnalyzed = document.getElementById('stat-analyzed');
const statBlocked = document.getElementById('stat-blocked');
const statPhishing = document.getElementById('stat-phishing');
const checkBtn = document.getElementById('check-gmail');

function setResult(message, isError = false) {
  resultEl.textContent = message;
  resultEl.style.color = isError ? '#ef4444' : '#64748b';
}

async function fetchStats() {
  try {
    const response = await fetch('http://localhost:8000/api/dashboard/stats', {
      headers: { 'X-User-Id': 'dashboard-user' }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    
    if (data && data.data) {
      statAnalyzed.textContent = data.data.total_emails_analyzed || 0;
      statBlocked.textContent = data.data.total_blocked || 0;
      statPhishing.textContent = data.data.total_phishing_detected || 0;
      
      statusEl.textContent = 'Connected';
      statusEl.style.color = '#10b981';
    }
  } catch (error) {
    statusEl.textContent = 'Offline';
    statusEl.style.color = '#ef4444';
  }
}

function injectGmailScript(tabId, callback) {
  if (!chrome.scripting) {
    callback(false, 'Scripting API unavailable.');
    return;
  }
  chrome.scripting.executeScript(
    {
      target: { tabId },
      files: ['content-scripts/gmail.js'],
    },
    () => {
      if (chrome.runtime.lastError) {
        callback(false, chrome.runtime.lastError.message);
        return;
      }
      callback(true);
    }
  );
}

function checkGmailTab() {
  checkBtn.textContent = 'Scanning...';
  checkBtn.style.opacity = '0.7';
  
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const restoreBtn = () => { checkBtn.textContent = 'Scan Current Gmail Tab'; checkBtn.style.opacity = '1'; };
    
    if (!tabs || !tabs.length) {
      setResult('No active tab found.', true);
      restoreBtn();
      return;
    }
    const tab = tabs[0];
    if (!tab.url || !tab.url.includes('mail.google.com')) {
      setResult('Please open Gmail to scan.', true);
      restoreBtn();
      return;
    }

    chrome.tabs.sendMessage(tab.id, { type: 'CHECK_GMAIL' }, (response) => {
      if (chrome.runtime.lastError) {
        setResult('Injecting script...', false);
        injectGmailScript(tab.id, (success, errorMessage) => {
          restoreBtn();
          if (!success) {
            setResult(`Failed: ${errorMessage}`, true);
            return;
          }
          setResult('Ready. Try scanning again.', false);
        });
        return;
      }
      restoreBtn();
      if (response?.success) {
        setResult('Scanner active on this tab.');
      } else {
        setResult('No response from tab.', true);
      }
    });
  });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'GMAIL_PONG') {
    setResult('Scanner listening.');
    sendResponse({ success: true });
  }
});

// Init
fetchStats();
setInterval(fetchStats, 5000);

checkBtn.addEventListener('click', checkGmailTab);
checkBtn.addEventListener('mouseover', () => checkBtn.style.backgroundColor = '#1d4ed8');
checkBtn.addEventListener('mouseout', () => checkBtn.style.backgroundColor = '#2563eb');

