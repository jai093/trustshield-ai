/**
 * Gmail Real-Time Phishing Detection Content Script
 * Uses trained model + Ollama API to analyze emails in real-time
 * Applies prevention actions: disable links, blur QR, show warning banner
 */

(() => {
const BACKEND_URL = 'http://localhost:8000';
const ANALYSIS_TIMEOUT = 5000;

class GmailPhishingDetector {
  constructor() {
    this.cache = new Map();
    this.analyzing = new Set();
    this.extensionId = chrome.runtime.id;
    this.initializeMutationObserver();
  }

  initializeMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const emailElements = node.querySelectorAll?.('[data-message-id]') || [];
            if (emailElements.length > 0) {
              emailElements.forEach((el) => this.analyzeEmailElement(el));
            }
            if (node.matches?.('[data-message-id]')) {
              this.analyzeEmailElement(node);
            }
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: false,
      characterData: false,
    });

    console.log('[TrustShield] Gmail phishing detector initialized');
  }

  async extractEmailFromDOM(element) {
    try {
      const messageId = element.getAttribute('data-message-id');
      if (!messageId) return null;

      const senderElement = element.querySelector('[email]');
      const sender = senderElement?.getAttribute('email') || 'unknown@unknown.com';
      const senderName = senderElement?.textContent?.trim() || '';

      const subjectElement = element.querySelector('[data-subject]') || document.querySelector('h2.hP');
      const subject = (subjectElement?.getAttribute('data-subject') || subjectElement?.textContent?.trim()) || 'No Subject';

      const bodyElement = element.querySelector('[data-body-message-id], .a3s, [role="article"] div');
      if (!bodyElement) {
        // Do not analyze if there is no email body (e.g., list view)
        return null; 
      }
      const body = bodyElement?.innerText || '';

      const links = Array.from(element.querySelectorAll('a[href]')).map((a) => ({
        text: a.textContent.trim(),
        href: a.href,
      }));

      const attachments = Array.from(
        element.querySelectorAll('[data-filename], [download]')
      ).map((el) => ({
        name: el.getAttribute('data-filename') || el.textContent?.trim() || 'attachment',
        size: 0,
      }));

      return {
        messageId,
        sender,
        senderName,
        subject,
        body,
        links,
        attachments,
        isSpamFolder: window.location.href.toLowerCase().includes('spam') || document.body.innerText.includes('Why is this message in spam?'),
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('[TrustShield] Error extracting email:', error);
      return null;
    }
  }

  async analyzeEmail(emailData) {
    const cacheKey = emailData.messageId;

    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < 3600000) {
        return cached.result;
      }
    }

    if (this.analyzing.has(cacheKey)) {
      return null;
    }

    this.analyzing.add(cacheKey);

    try {
      const result = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          { type: 'ANALYZE_EMAIL', data: emailData },
          (response) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
              return;
            }
            if (!response || !response.success) {
              reject(new Error(response?.error || 'Unknown error from background script'));
              return;
            }
            
            // Reconstruct the expected response format that applyPreventionActions expects
            resolve({
              success: true,
              data: response.analysis
            });
          }
        );
      });

      this.cache.set(cacheKey, {
        result,
        timestamp: Date.now(),
      });

      return result;
    } catch (error) {
      console.error('[TrustShield] Analysis error:', error);
      if (error.message && error.message.includes("Extension context invalidated")) {
        alert("TrustShield AI was just updated with new security rules!\n\nPlease REFRESH this Gmail page (Press F5) to apply the update and scan this email.");
      }
      return null;
    } finally {
      this.analyzing.delete(cacheKey);
    }
  }

  applyPreventionActions(element, analysis) {
    if (!analysis || !analysis.data) return;

    const data = analysis.data;
    const riskScore = data.risk_score || 0;
    const suggestedAction = data.suggested_action?.toLowerCase();
    
    // Check if any prevention action suggests disabling
    const shouldDisable = riskScore >= 70 || 
                         suggestedAction === 'block' || 
                         (data.prevention_actions && data.prevention_actions.some(a => ['DISABLE_LINK', 'DISABLE_BUTTONS', 'BLOCK_DOWNLOADS'].includes(a.type)));

    this.addWarningBanner(element, data, riskScore);

    if (shouldDisable) {
      this.disableLinksInEmail(element);
      this.addRiskHighlight(element, 'HIGH', riskScore);
    } else if (riskScore >= 50 && riskScore < 70) {
      this.addRiskHighlight(element, 'MEDIUM', riskScore);
    }
  }

  addWarningBanner(element, data, riskScore) {
    if (element.querySelector('[data-trustshield-banner]')) return;

    const colorMap = {
      HIGH: '#d32f2f',
      MEDIUM: '#f57c00',
      LOW: '#388e3c',
      CRITICAL: '#b71c1c',
    };

    const banner = document.createElement('div');
    banner.setAttribute('data-trustshield-banner', 'true');
    banner.style.cssText = `
      background-color: ${colorMap[data.risk_level] || '#d32f2f'};
      color: white;
      padding: 12px 16px;
      margin-bottom: 12px;
      border-radius: 4px;
      font-size: 14px;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    `;

    const icon = document.createElement('span');
    icon.textContent = 'Warning';

    const message = document.createElement('span');
    message.innerHTML = `
      <strong>TrustShield Alert:</strong> Risk Score: ${riskScore}% - ${data.threat_category}
    `;

    banner.appendChild(icon);
    banner.appendChild(message);

    // Find a reliable place to insert the banner
    let insertTarget = element.querySelector('.nH.hx') || // Header area in expanded email
                       element.querySelector('.gE.iv.gt') || // Another common header class
                       element.querySelector('[data-body-message-id]')?.parentElement ||
                       element.querySelector('.a3s')?.parentElement ||
                       element.querySelector('[role="article"]');
                       
    if (!insertTarget) {
      insertTarget = element; // Fallback
    }

    insertTarget.insertBefore(banner, insertTarget.firstChild);
  }

  disableLinksInEmail(element) {
    // Disable all links
    const links = element.querySelectorAll('a[href]');
    links.forEach((link) => {
      const originalHref = link.href;
      link.dataset.originalHref = originalHref;
      link.removeAttribute('href');
      link.style.pointerEvents = 'none';
      link.style.opacity = '0.5';
      link.style.color = '#999';
      link.title = `Disabled: ${originalHref}`;
    });
    
    // Disable all images to prevent tracking pixels / malicious QR codes
    const images = element.querySelectorAll('img');
    images.forEach((img) => {
      img.style.filter = 'blur(10px)';
      img.title = 'Image blocked by TrustShield';
    });
    
    // Disable all buttons
    const buttons = element.querySelectorAll('button, [role="button"]');
    buttons.forEach((btn) => {
      btn.disabled = true;
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.5';
    });
  }

  addRiskHighlight(element, riskLevel, riskScore) {
    const colorMap = {
      HIGH: '#ffebee',
      MEDIUM: '#fff3e0',
      LOW: '#e8f5e9',
    };

    element.style.borderLeft = `4px solid ${colorMap[riskLevel] || '#d32f2f'}`;
    element.style.backgroundColor = colorMap[riskLevel];
  }

  async analyzeEmailElement(element) {
    const messageId = element.getAttribute('data-message-id');
    if (!messageId) return;

    const emailData = await this.extractEmailFromDOM(element);
    if (!emailData) return;

    const analysis = await this.analyzeEmail(emailData);
    if (!analysis) return;

    this.applyPreventionActions(element, analysis);
  }
}

function initDetector() {
  const detector = new GmailPhishingDetector();
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'CHECK_GMAIL') {
      const emailElements = document.querySelectorAll('[data-message-id]');
      emailElements.forEach(el => detector.analyzeEmailElement(el));
      sendResponse({ success: true });
    } else if (request.type === 'GMAIL_PONG') {
      sendResponse({ success: true });
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDetector);
} else {
  initDetector();
}
})();
