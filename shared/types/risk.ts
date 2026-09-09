/**
 * Risk Analysis types shared across the system
 */

export enum ThreatCategory {
  NONE = "NONE",
  CREDENTIAL_THEFT = "CREDENTIAL_THEFT",
  FINANCIAL_FRAUD = "FINANCIAL_FRAUD",
  INVOICE_SCAM = "INVOICE_SCAM",
  GIFT_CARD_SCAM = "GIFT_CARD_SCAM",
  BANK_SCAM = "BANK_SCAM",
  CRYPTO_SCAM = "CRYPTO_SCAM",
  MALWARE_DELIVERY = "MALWARE_DELIVERY",
  FAKE_VERIFICATION = "FAKE_VERIFICATION",
  PASSWORD_RESET_SCAM = "PASSWORD_RESET_SCAM",
  BRAND_IMPERSONATION = "BRAND_IMPERSONATION",
  BEC = "BEC", // Business Email Compromise
}

export enum ActionType {
  ALLOW = "ALLOW",
  WARN = "WARN",
  BLOCK = "BLOCK",
  REWRITE = "REWRITE",
  REPORT = "REPORT",
}

export interface AgentScore {
  agentName: string;
  score: number; // 0-100
  confidence: number; // 0-1
  reasons: string[];
  evidence: Record<string, any>;
}

export interface RiskAnalysis {
  // Overall Risk
  overallRiskScore: number; // 0-100
  riskLevel: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  confidence: number; // 0-1
  threatCategory: ThreatCategory;
  
  // Individual Agent Scores
  agentScores: {
    emailExtraction: AgentScore;
    brandVerification: AgentScore;
    intentDetection: AgentScore;
    urlIntelligence: AgentScore;
    psychologyManipulation: AgentScore;
    qrDetection: AgentScore;
    attachmentAnalysis: AgentScore;
  };
  
  // Decision
  suggestedAction: ActionType;
  preventionActions: PreventionAction[];
  
  // Explanation
  explanation: string;
  detailedReasons: string[];
  
  // Metadata
  analyzedAt: string;
  processingTimeMs: number;
  localAnalysisOnly?: boolean;
}

export interface PreventionAction {
  type: "DISABLE_LINK" | "DISABLE_BUTTON" | "BLUR_IMAGE" | "BLUR_QR" | "HIDE_ATTACHMENT" | "BLOCK_FORM";
  targetSelector?: string;
  element?: HTMLElement;
  reason: string;
}

export interface BrandScore {
  brandName: string;
  impersonationProbability: number; // 0-1
  indicators: {
    senderDomainMatch: number;
    logoMatch: number;
    writingStyleMatch: number;
    colorSchemeMatch: number;
  };
  evidence: string[];
}

export interface URLAnalysis {
  url: string;
  riskScore: number; // 0-100
  indicators: {
    domainAge?: number;
    isTyposquatting: boolean;
    isShortened: boolean;
    hasRedirects: boolean;
    sslValid: boolean;
    ipReputation: number;
  };
  suspiciousTlds: string[];
  evidence: string[];
}

export interface AttachmentRisk {
  fileName: string;
  riskScore: number; // 0-100
  risks: {
    doubleExtension: boolean;
    macroEnabled: boolean;
    executable: boolean;
    passwordProtected: boolean;
    suspiciousExtension: boolean;
  };
  evidence: string[];
}
