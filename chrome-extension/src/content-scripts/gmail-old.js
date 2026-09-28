/**
 * Gmail Real-Time Phishing Detection Content Script
 * Uses trained model + Ollama API to analyze emails in real-time
 * Applies prevention actions: disable links, blur QR, show warning banner
 */

const BACKEND_URL = 'https://trustshield-ai-coh2.onrender.com';
const ANALYSIS_TIMEOUT = 5000; // 5 seconds
const EMAIL_SELECTOR = '[data-message-id]'; // Gmail email container
const CACHE_KEY = 'trustshield_email_analysis_cache';

class GmailPhishingDetector {
  constructor() {
    this.cache = new Map();
    this.analyzing = new Set();
    this.extensionId = chrome.runtime.id;
    this.initializeMutationObserver();
  }

  /**
   * Set up MutationObserver to watch for new emails in Gmail
   */
  initializeMutationObserver() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if new email element added
            const emailElements = node.querySelectorAll?.(EMAIL_SELECTOR) || [];
            if (emailElements.length > 0) {
              emailElements.forEach((el) => this.analyzeEmailElement(el));
            }
            // Direct match
            if (node.matches?.(EMAIL_SELECTOR)) {
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

  /**
   * Extract email data from Gmail DOM element
   */
  async extractEmailFromDOM(element) {
    try {
      // Get email metadata from Gmail's data attributes
      const messageId = element.getAttribute('data-message-id');
      if (!messageId) return null;

      // Extract sender info
      const senderElement = element.querySelector('[email]');
      const sender = senderElement?.getAttribute('email') || 'unknown@unknown.com';
      const senderName = senderElement?.textContent?.trim() || '';

      // Extract subject
      const subjectElement = element.querySelector('[data-subject]');
      const subject = subjectElement?.getAttribute('data-subject') || 'No Subject';

      // Extract body - Gmail stores body in a specific container
      const bodyElement = element.querySelector('[data-body-message-id], [role="article"] div');
      const body = bodyElement?.innerText || '';

      // Extract links
      const links = Array.from(element.querySelectorAll('a[href]')).map((a) => ({
        text: a.textContent.trim(),
        href: a.href,
      }));

      // Extract attachments
      const attachments = Array.from(
        element.querySelectorAll('[data-filename], .goog-date-editor, [download]')
      ).map((el) => ({
        filename: el.getAttribute('data-filename') || el.textContent?.trim() || 'attachment',
        size: el.getAttribute('data-size') || 'unknown',
      }));

      return {
        messageId,
        sender,
        senderName,
        subject,
        body,
        links,
        attachments,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      console.error('[TrustShield] Error extracting email:', error);
      return null;
    }
  }

  /**
   * Analyze email using backend analysis service
   */
  async analyzeEmail(emailData) {
    const cacheKey = `${emailData.sender}:${emailData.subject}`;

    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < 3600000) {
        // Cache valid for 1 hour
        return cached.result;
      }
    }

    // Prevent duplicate analysis
    if (this.analyzing.has(cacheKey)) {
      return null;
    }

    this.analyzing.add(cacheKey);

    try {
      const response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Extension-ID': this.extensionId,
        },
        body: JSON.stringify({
          sender: emailData.sender,
          sender_name: emailData.senderName,
          subject: emailData.subject,
          body: emailData.body,
          links: emailData.links,
          attachments: emailData.attachments,
          timestamp: emailData.timestamp,
        }),
        signal: AbortSignal.timeout(ANALYSIS_TIMEOUT),
      });

      if (!response.ok) {
        console.warn('[TrustShield] Analysis API returned:', response.status);
        return null;
      }

      const result = await response.json();

      // Cache result
      this.cache.set(cacheKey, {
        result,
        timestamp: Date.now(),
      });

      return result;
    } catch (error) {
      console.error('[TrustShield] Analysis error:', error);
      return null;
    } finally {
      this.analyzing.delete(cacheKey);
    }
  }

  /**
   * Apply prevention actions to email element
   */
  applyPreventionActions(element, analysis) {
    if (!analysis || !analysis.risk_score) return;

    const riskScore = analysis.risk_score;
    const preventionActions = analysis.prevention_actions || [];

    // Determine UI treatment based on risk level
    const isHighRisk = riskScore >= 70;
    const isMediumRisk = riskScore >= 50;
    const isLowRisk = riskScore < 50;

    // 1. Add warning banner
    this.addWarningBanner(element, analysis, riskScore);

    // 2. If HIGH RISK: disable links and add visual warnings
    if (isHighRisk) {
      this.disableLinksInEmail(element, preventionActions);
      this.disableAttachmentDownloads(element, preventionActions);
      this.addRiskHighlight(element, 'HIGH', riskScore);
    }

    // 3. If MEDIUM RISK: show warning but allow user choice
    if (isMediumRisk && !isHighRisk) {
      this.addRiskHighlight(element, 'MEDIUM', riskScore);
      this.warnAboutSuspiciousLinks(element, preventionActions);
    }

    // 4. Blur QR codes if present
    if (preventionActions.includes('blur_qr')) {
      this.blurQRCodes(element);
    }

    // 5. Send report to backend
    this.reportAnalysis(analysis);
  }

  /**
   * Add warning banner at top of email
   */
  addWarningBanner(element, analysis, riskScore) {
    // Avoid duplicates
    if (element.querySelector('[data-trustshield-banner]')) return;

    const threatCategory = analysis.threat_category || 'unknown_threat';
    const riskLevel = analysis.risk_level || 'UNKNOWN';
    const colorMap = {
      HIGH: '#d32f2f',
      MEDIUM: '#f57c00',
      LOW: '#388e3c',
      CRITICAL: '#b71c1c',
    };

    const banner = document.createElement('div');
    banner.setAttribute('data-trustshield-banner', 'true');
    banner.style.cssText = `
      background-color: ${colorMap[riskLevel] || '#d32f2f'};
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
    icon.textContent = '⚠️';
    icon.style.fontSize = '18px';

    const message = document.createElement('span');
    message.innerHTML = `
      <strong>TrustShield Alert:</strong> This email appears to be <strong>${threatCategory}</strong> 
      (Risk: ${riskScore}%) - ${analysis.suggested_action || 'Please review carefully'}
    `;

    banner.appendChild(icon);
    banner.appendChild(message);

    // Insert at top of email body
    const emailBody = element.querySelector('[data-body-message-id], [role="article"]');
    if (emailBody) {
      emailBody.insertBefore(banner, emailBody.firstChild);
    }
  }

  /**
   * Disable all links in suspicious email
   */
  disableLinksInEmail(element, preventionActions) {
    if (!preventionActions.includes('disable_links')) return;

    const links = element.querySelectorAll('a[href]');
    links.forEach((link) => {
      // Replace href to prevent accidental clicks
      const originalHref = link.href;
      link.dataset.originalHref = originalHref;
      link.removeAttribute('href');

      // Disable pointer events
      link.style.pointerEvents = 'none';
      link.style.opacity = '0.5';
      link.style.cursor = 'default';
      link.style.textDecoration = 'line-through';
      link.style.color = '#999';

      // Add tooltip
      link.title = `Link disabled by TrustShield: ${originalHref}`;

      // Show disabled badge
      const badge = document.createElement('span');
      badge.textContent = ' [DISABLED]';
      badge.style.color = '#d32f2f';
      badge.style.fontWeight = 'bold';
      badge.style.fontSize = '12px';
      link.appendChild(badge);
    });
  }

  /**
   * Disable attachment downloads in high-risk emails
   */
  disableAttachmentDownloads(element, preventionActions) {
    if (!preventionActions.includes('disable_downloads')) return;

    const downloadButtons = element.querySelectorAll('[download], [data-filename]');
    downloadButtons.forEach((btn) => {
      btn.style.pointerEvents = 'none';
      btn.style.opacity = '0.5';
      btn.style.cursor = 'default';
      btn.title = 'Download disabled by TrustShield - suspected malicious attachment';

      const badge = document.createElement('span');
      badge.textContent = ' [BLOCKED]';
      badge.style.color = '#d32f2f';
      badge.style.fontWeight = 'bold';
      badge.style.marginLeft = '4px';
      btn.appendChild(badge);
    });
  }

  /**
   * Blur QR codes in email
   */
  blurQRCodes(element) {
    const images = element.querySelectorAll('img[src]');
    images.forEach((img) => {
      // Simple heuristic: square images might be QR codes
      if (img.width && img.height && Math.abs(img.width - img.height) < 10) {
        img.style.filter = 'blur(8px)';
        img.style.cursor = 'pointer';
        img.title = 'QR code blurred by TrustShield';

        // Unblur on click
        img.addEventListener('click', function (e) {
          if (this.style.filter === 'blur(8px)') {
            this.style.filter = 'none';
            this.title = 'Click again to blur';
          } else {
            this.style.filter = 'blur(8px)';
            this.title = 'QR code blurred by TrustShield';
          }
          e.stopPropagation();
        });
      }
    });
  }

  /**
   * Add visual risk highlighting to email container
   */
  addRiskHighlight(element, riskLevel, riskScore) {
    const colorMap = {
      HIGH: '#ffebee',
      MEDIUM: '#fff3e0',
      LOW: '#e8f5e9',
      CRITICAL: '#b71c1c',
    };

    element.style.borderLeft = `4px solid ${colorMap[riskLevel] || '#d32f2f'}`;
    element.style.paddingLeft = '12px';
    element.style.backgroundColor = colorMap[riskLevel];
  }

  /**
   * Warn about suspicious links without disabling
   */
  warnAboutSuspiciousLinks(element, preventionActions) {
    const links = element.querySelectorAll('a[href]');
    links.forEach((link) => {
      if (!link.dataset.trustshieldWarned) {
        link.dataset.trustshieldWarned = 'true';
        link.style.position = 'relative';

        // Add warning badge
        const warning = document.createElement('span');
        warning.textContent = '⚠️';
        warning.style.position = 'absolute';
        warning.style.right = '-10px';
        warning.style.top = '-10px';
        warning.style.backgroundColor = '#f57c00';
        warning.style.borderRadius = '50%';
        warning.style.width = '20px';
        warning.style.height = '20px';
        warning.style.display = 'flex';
        warning.style.alignItems = 'center';
        warning.style.justifyContent = 'center';
        warning.style.cursor = 'help';
        warning.title = 'Potentially suspicious link - verify before clicking';

        link.parentElement.style.position = 'relative';
        link.parentElement.appendChild(warning);
      }
    });
  }

  /**
   * Send analysis report to backend
   */
  async reportAnalysis(analysis) {
    try {
      await fetch(`${BACKEND_URL}/api/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Extension-ID': this.extensionId,
        },
        body: JSON.stringify({
          email_id: analysis.email_id || 'unknown',
          risk_level: analysis.risk_level,
          threat_category: analysis.threat_category,
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (error) {
      console.error('[TrustShield] Error reporting analysis:', error);
    }
  }

  /**
   * Analyze email element in DOM
   */
  async analyzeEmailElement(element) {
    const messageId = element.getAttribute('data-message-id');
    if (!messageId) return;

    // Extract email data
    const emailData = await this.extractEmailFromDOM(element);
    if (!emailData) return;

    // Analyze via backend
    const analysis = await this.analyzeEmail(emailData);
    if (!analysis) return;

    // Apply prevention actions
    this.applyPreventionActions(element, analysis);
  }
}

// Initialize detector when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new GmailPhishingDetector();
  });
} else {
  new GmailPhishingDetector();
}
    document.querySelectorAll('[role="link"][aria-label*="Download"]').forEach(att => {
      attachments.push({
        name: att.getAttribute('aria-label'),
        size: 0
      });
    });
    email.attachments = attachments;

    // Extract images
    const images = [];
    document.querySelectorAll('img').forEach(img => {
      if (img.src && !img.src.startsWith('data:image/gif')) {
        images.push({
          src: img.src,
          alt: img.alt,
          width: img.width,
          height: img.height
        });
      }
    });
    email.images = images;

    email.extractedAt = new Date().toISOString();
    return email;
  }

  isAccountChooserFlow() {
    const locationString = `${window.location.search || ''}${window.location.hash || ''}`;
    return locationString.includes('flowName=GlifWebSignIn') || locationString.includes('flowEntry=AccountChooser');
  }

  isVisibleElement(element) {
    if (!element || !(element instanceof Element)) return false;
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && style.visibility !== 'hidden' && element.offsetWidth > 0 && element.offsetHeight > 0;
  }

  isSignInPage() {
    const emailInput = document.querySelector('input[type="email"]');
    const passwordInput = document.querySelector('input[type="password"]');
    const signInForm = document.querySelector('form[action*="signin"]');

    return Boolean(
      this.isAccountChooserFlow() ||
      (emailInput && this.isVisibleElement(emailInput)) ||
      (passwordInput && this.isVisibleElement(passwordInput)) ||
      (signInForm && this.isVisibleElement(signInForm))
    );
  }

  getMessageContainer() {
    return (
      document.querySelector('[role="presentation"]') ||
      document.querySelector('div.a3s') ||
      document.querySelector('.ii.gt')
    );
  }

  getSenderElement(messageContainer) {
    return (
      messageContainer?.querySelector('span[email]') ||
      document.querySelector('span[email]') ||
      document.querySelector('.gD')
    );
  }

  getSubjectElement(messageContainer) {
    return (
      messageContainer?.querySelector('h2[data-subject]') ||
      messageContainer?.querySelector('h2.hP') ||
      document.querySelector('h2.hP') ||
      document.querySelector('h2[data-subject]')
    );
  }

  hasGmailMessageView() {
    const messagePanel = this.getMessageContainer();
    const sender = this.getSenderElement(messagePanel);
    const subject = this.getSubjectElement(messagePanel);
    return Boolean(messagePanel && sender && subject && this.isVisibleElement(messagePanel));
  }

  isGmailUIReady() {
    return Boolean(
      document.querySelector('div[role="main"]') &&
      document.querySelector('div[role="navigation"]')
    );
  }

  disconnectObserver() {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = null;
    }

    if (this.observer) {
      try {
        this.observer.disconnect();
      } catch (error) {
        console.warn('TrustShield AI: disconnectObserver failed', error);
      }
      this.observer = null;
    }

    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }

    this.observing = false;
  }

  setupUrlPolling() {
    if (this.checkInterval) return;

    this.checkInterval = window.setInterval(() => {
      if (window.location.href !== this.currentUrl) {
        this.currentUrl = window.location.href;
        this.disconnectObserver();
        this.startMonitoring();
      }
    }, 1000);
  }

  scheduleRestart() {
    if (this.restartScheduled) return;
    this.restartScheduled = true;

    const restart = () => {
      this.restartScheduled = false;
      this.startMonitoring();
    };

    ['hashchange', 'popstate', 'visibilitychange', 'pagehide', 'DOMContentLoaded'].forEach(event => {
      window.addEventListener(event, restart, { once: true });
    });

    if (this.restartTimer) {
      clearTimeout(this.restartTimer);
    }

    this.restartTimer = window.setTimeout(() => {
      this.restartTimer = null;
      this.restartScheduled = false;
      this.startMonitoring();
    }, 2000);
  }

  getEmailSignature(email) {
    return [email.sender, email.subject, email.body?.slice(0, 200), email.htmlBody?.slice(0, 200)].filter(Boolean).join('::');
  }

  /**
   * Start monitoring for new emails using MutationObserver
   */
  startMonitoring() {
    if (this.observing && this.observer) return;

    if (!this.isGmailUIReady() || this.isSignInPage()) {
      this.disconnectObserver();
      this.scheduleRestart();
      return;
    }

    const targetNode = document.body || document.documentElement;
    if (!targetNode || !(targetNode instanceof Node)) {
      this.disconnectObserver();
      this.scheduleRestart();
      return;
    }

    const observer = new MutationObserver((mutations) => {
      if (document.hidden) {
        return;
      }

      if (this.isAccountChooserFlow()) {
        this.disconnectObserver();
        this.scheduleRestart();
        return;
      }

      if (!this.hasGmailMessageView()) {
        return;
      }

      if (!mutations.some(m => m.addedNodes.length > 0 || m.type === 'childList' || m.type === 'attributes')) {
        return;
      }

      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer);
      }

      this.debounceTimer = window.setTimeout(() => {
        this.debounceTimer = null;
        this.onEmailDetected();
      }, 300);
    });

    try {
      observer.observe(targetNode, {
        childList: true,
        subtree: true,
        attributes: true
      });
    } catch (error) {
      console.warn('TrustShield AI: MutationObserver failed', error);
      return;
    }

    this.observer = observer;
    this.observing = true;
    this.setupUrlPolling();

    if (this.hasGmailMessageView()) {
      window.setTimeout(() => this.onEmailDetected(), 300);
    }

    window.addEventListener('beforeunload', () => this.disconnectObserver(), { once: true });
  }

  /**
   * Called when new email is detected
   */
  isEmailViewOpen() {
    return this.hasGmailMessageView();
  }

  onEmailDetected() {
    try {
      if (this.isSignInPage() || !this.isEmailViewOpen()) {
        return;
      }

      if (this.isAccountChooserFlow()) {
        return;
      }

      if (this.isAccountChooserFlow()) {
        return;
      }

      const email = this.extractEmailContent();
      const emailHash = this.getEmailSignature(email);
      if (!emailHash || emailHash === this.lastEmailHash) {
        return;
      }
      this.lastEmailHash = emailHash;

      if (!email.sender && !email.subject && !email.body && !email.htmlBody) {
        return;
      }

      chrome.runtime.sendMessage({
        type: 'ANALYZE_EMAIL',
        data: email
      }, response => {
        try {
          if (chrome.runtime.lastError) {
            console.warn('TrustShield AI: sendMessage failed', chrome.runtime.lastError);
            if (chrome.runtime.lastError.message?.includes('Extension context invalidated')) {
              this.disconnectObserver();
              this.scheduleRestart();
            }
            return;
          }

          if (response && response.analysis) {
            this.applyPreventionActions(response.analysis);
          }
        } catch (callbackError) {
          console.warn('TrustShield AI: runtime callback failed', callbackError);
        }
      });
    } catch (error) {
      console.warn('TrustShield AI: onEmailDetected failed', error);
    }
  }

  /**
   * Apply prevention actions to email DOM
   */
  applyPreventionActions(analysis) {
    const { risk_score, prevention_actions } = analysis;

    prevention_actions?.forEach(action => {
      switch (action.type) {
        case 'DISABLE_LINK':
          this.disableLink(action.target);
          break;
        case 'DISABLE_BUTTONS':
          this.disableButtons();
          break;
        case 'BLUR_QR':
          this.blurQRCodes();
          break;
        case 'WARN_BANNER':
          this.showWarningBanner(analysis);
          break;
      }
    });

    // Always show analysis result
    if (risk_score > 25) {
      this.showAnalysisOverlay(analysis);
    }
  }

  /**
   * Disable suspicious links
   */
  disableLink(url) {
    document.querySelectorAll(`a[href="${url}"]`).forEach(link => {
      link.style.pointerEvents = 'none';
      link.style.opacity = '0.5';
      link.title = 'Suspicious link disabled by TrustShield AI';
    });
  }

  /**
   * Disable all buttons/CTAs
   */
  disableButtons() {
    document.querySelectorAll('a, button').forEach(btn => {
      if (btn.textContent.toLowerCase().includes('confirm') ||
          btn.textContent.toLowerCase().includes('verify')) {
        btn.style.pointerEvents = 'none';
        btn.style.opacity = '0.6';
      }
    });
  }

  /**
   * Blur QR codes
   */
  blurQRCodes() {
    document.querySelectorAll('img').forEach(img => {
      if (img.alt?.toLowerCase().includes('qr') ||
          img.src?.includes('qr')) {
        img.style.filter = 'blur(10px)';
        img.title = 'Suspicious QR code blurred by TrustShield AI';
      }
    });
  }

  /**
   * Show warning banner
   */
  showWarningBanner(analysis) {
    const banner = document.createElement('div');
    banner.className = 'trustshield-warning-banner';
    banner.innerHTML = `
      <div class="warning-content">
        <span class="warning-icon">⚠️</span>
        <div class="warning-message">
          <strong>TrustShield AI Alert:</strong>
          ${analysis.explanation}
          <details>
            <summary>View details</summary>
            <ul>
              ${analysis.detailed_reasons.map(r => `<li>${r}</li>`).join('')}
            </ul>
          </details>
        </div>
        <button class="dismiss-btn">Dismiss</button>
      </div>
    `;
    
    document.body.insertBefore(banner, document.body.firstChild);
    
    banner.querySelector('.dismiss-btn').addEventListener('click', () => {
      banner.remove();
    });
  }

  /**
   * Show detailed analysis overlay
   */
  showAnalysisOverlay(analysis) {
    const overlay = document.createElement('div');
    overlay.className = 'trustshield-analysis-overlay';
    overlay.innerHTML = `
      <div class="analysis-card">
        <div class="analysis-header">
          <h3>TrustShield AI Analysis</h3>
          <button class="close-btn">&times;</button>
        </div>
        <div class="analysis-body">
          <div class="risk-score" style="color: ${this.getRiskColor(analysis.risk_score)}">
            Risk Score: ${analysis.risk_score}/100
          </div>
          <div class="risk-level">${analysis.risk_level}</div>
          <div class="threat-category">Type: ${analysis.threat_category}</div>
          <div class="explanation">${analysis.explanation}</div>
        </div>
      </div>
    `;
    
    document.body.appendChild(overlay);
    overlay.querySelector('.close-btn').addEventListener('click', () => {
      overlay.remove();
    });
  }

  /**
   * Get color for risk score
   */
  getRiskColor(score) {
    if (score >= 75) return '#d32f2f';     // RED
    if (score >= 50) return '#f57c00';     // ORANGE
    if (score >= 25) return '#fbc02d';     // YELLOW
    return '#388e3c';                       // GREEN
  }
}

// Initialize on page load
const extractor = new GmailEmailExtractor();
extractor.startMonitoring();

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request?.type === 'CHECK_GMAIL') {
    sendResponse({ success: true });
  }
});

console.log('TrustShield AI: Gmail content script loaded');
