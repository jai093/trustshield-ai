const app = document.getElementById('app');
app.style.fontFamily = 'Arial, sans-serif';
app.style.padding = '16px';
app.style.minWidth = '320px';

app.innerHTML = `
  <div style="display: flex; flex-direction: column; gap: 14px;">
    <div>
      <h1 style="margin: 0 0 8px;">TrustShield AI Options</h1>
      <p style="margin: 0; color: #555;">Configure the backend endpoint and trust settings.</p>
    </div>
    <label style="display: flex; flex-direction: column; gap: 6px;">
      <span>Backend API endpoint</span>
      <input id="api-endpoint" type="text" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ccc;" />
    </label>
    <label style="display: flex; align-items: center; gap: 8px;">
      <input id="enable-analysis" type="checkbox" />
      <span>Enable backend analysis</span>
    </label>
    <label style="display: flex; flex-direction: column; gap: 6px;">
      <span>Risk threshold</span>
      <input id="risk-threshold" type="number" min="0" max="100" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ccc;" />
    </label>
    <button id="save-settings" style="padding: 10px 14px; border: none; border-radius: 8px; background: #1a73e8; color: white; cursor: pointer;">Save Settings</button>
    <div id="status" style="color: #333;"></div>
  </div>
`;

const apiInput = document.getElementById('api-endpoint');
const enableCheckbox = document.getElementById('enable-analysis');
const thresholdInput = document.getElementById('risk-threshold');
const statusEl = document.getElementById('status');

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? '#d93025' : '#202124';
}

chrome.storage.sync.get({
  apiEndpoint: 'http://localhost:8000',
  enableBackendAnalysis: false,
  riskThreshold: 50
}, (values) => {
  apiInput.value = values.apiEndpoint;
  enableCheckbox.checked = values.enableBackendAnalysis;
  thresholdInput.value = values.riskThreshold;
});

function saveSettings() {
  const apiEndpoint = apiInput.value.trim() || 'http://localhost:8000';
  const enableBackendAnalysis = enableCheckbox.checked;
  const riskThreshold = Number(thresholdInput.value) || 50;

  chrome.storage.sync.set({ apiEndpoint, enableBackendAnalysis, riskThreshold }, () => {
    setStatus('Settings saved.');
  });
}

document.getElementById('save-settings').addEventListener('click', saveSettings);
