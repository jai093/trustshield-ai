const app = document.getElementById('app');
app.style.fontFamily = 'Arial, sans-serif';
app.style.padding = '20px';
app.style.maxWidth = '480px';

app.innerHTML = `
  <div style="display: flex; flex-direction: column; gap: 14px;">
    <div>
      <h1 style="margin: 0 0 6px; font-size: 20px;">🛡️ TrustShield AI Options</h1>
      <p style="margin: 0; color: #555; font-size: 13px;">Configure your backend endpoint, threshold, and trusted college email domains.</p>
    </div>
    
    <label style="display: flex; flex-direction: column; gap: 6px;">
      <span style="font-weight: 600; font-size: 13px;">Backend API Endpoint</span>
      <input id="api-endpoint" type="text" style="width: 100%; box-sizing: border-box; padding: 10px; border-radius: 8px; border: 1px solid #ccc;" />
    </label>

    <label style="display: flex; align-items: center; gap: 8px;">
      <input id="enable-analysis" type="checkbox" />
      <span style="font-size: 13px;">Enable backend real-time analysis</span>
    </label>

    <label style="display: flex; flex-direction: column; gap: 6px;">
      <span style="font-weight: 600; font-size: 13px;">Risk Threshold (0-100)</span>
      <input id="risk-threshold" type="number" min="0" max="100" style="width: 100%; box-sizing: border-box; padding: 10px; border-radius: 8px; border: 1px solid #ccc;" />
    </label>

    <label style="display: flex; flex-direction: column; gap: 6px;">
      <span style="font-weight: 600; font-size: 13px;">Trusted College & Organizational Domains (Comma-separated)</span>
      <textarea id="trusted-domains" rows="3" placeholder="sairamce.edu.in, placement@sairamce.edu.in, edu.in, annauniv.edu" style="width: 100%; box-sizing: border-box; padding: 10px; border-radius: 8px; border: 1px solid #ccc; font-family: inherit; font-size: 12px;"></textarea>
      <span style="font-size: 11px; color: #666;">Emails from these domains will be verified as safe and will not trigger false phishing alarms.</span>
    </label>

    <button id="save-settings" style="padding: 10px 14px; border: none; border-radius: 8px; background: #1a73e8; color: white; font-weight: 600; cursor: pointer;">Save Settings</button>
    <div id="status" style="font-size: 13px; font-weight: 500;"></div>
  </div>
`;

const apiInput = document.getElementById('api-endpoint');
const enableCheckbox = document.getElementById('enable-analysis');
const thresholdInput = document.getElementById('risk-threshold');
const trustedDomainsInput = document.getElementById('trusted-domains');
const statusEl = document.getElementById('status');

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? '#d93025' : '#2e7d32';
}

chrome.storage.sync.get({
  apiEndpoint: 'https://trustshield-ai-coh2.onrender.com',
  enableBackendAnalysis: false,
  riskThreshold: 50,
  trustedDomains: ['sairamce.edu.in', 'placement@sairamce.edu.in', 'sairam.edu.in']
}, (values) => {
  apiInput.value = values.apiEndpoint;
  enableCheckbox.checked = values.enableBackendAnalysis;
  thresholdInput.value = values.riskThreshold;
  trustedDomainsInput.value = Array.isArray(values.trustedDomains) 
    ? values.trustedDomains.join(', ') 
    : (values.trustedDomains || 'sairamce.edu.in, placement@sairamce.edu.in');
});

function saveSettings() {
  const apiEndpoint = apiInput.value.trim() || 'https://trustshield-ai-coh2.onrender.com';
  const enableBackendAnalysis = enableCheckbox.checked;
  const riskThreshold = Number(thresholdInput.value) || 50;
  const trustedDomains = trustedDomainsInput.value
    .split(',')
    .map(d => d.trim().toLowerCase())
    .filter(Boolean);

  chrome.storage.sync.set({ apiEndpoint, enableBackendAnalysis, riskThreshold, trustedDomains }, () => {
    setStatus('✓ Settings saved successfully.');
  });
}

document.getElementById('save-settings').addEventListener('click', saveSettings);
